import pytest
import random
import string
import time
from pprint import pprint

from deltawoot.recv import get_leave_msg
from deltachat_rpc_client.const import ChatType

@pytest.mark.timeout(30)
def test_send_message(delta, woot, lp):
    text = "".join(random.choices(string.ascii_lowercase, k=9))

    lp.sec(f"Sending message '{text}' with Delta Chat")
    dcontact = delta.create_contact(woot.addr)
    dchat = dcontact.create_chat()
    dchat.send_text(text)

    wcontact = woot.create_contact_if_not_exists(delta.get_config('addr'), delta.get_config('displayname'))
    wconversation = woot.create_conversation_if_not_exists(wcontact)

    lp.sec("Polling for new messages in Chatwoot")
    while len(woot.get_messages(wconversation)) < 2:
        lp.sec("printing contact")
        pprint(woot.create_contact_if_not_exists(delta.get_config('addr'), delta.get_config('displayname')))
        lp.sec("printing conversation")
        pprint(woot.create_conversation_if_not_exists(wcontact))
        lp.sec("printing messages")
        pprint(woot.get_messages(wconversation))
        time.sleep(10)

    assert woot.get_messages(wconversation)[-1]['content'] == text

    lp.sec("Responding in Chatwoot")
    text2 = "".join(random.choices(string.ascii_lowercase, k=9))
    woot.send_message(
        conversation=wconversation,
        content=text2,
        message_type='outgoing'
    )

    lp.sec("Waiting for new messages in Delta")
    msg = delta.wait_for_incoming_msg()
    assert msg.get_snapshot().text == text2


@pytest.mark.timeout(30)
def test_leave_groups(delta, woot, lp):
    lp.sec("Creating Group")
    dgroup = delta.create_group("You don't want to be in here")

    lp.sec("Adding bot to it")
    dcontact = delta.create_contact(woot.addr)
    dgroup.add_contact(dcontact)
    snapshot = dgroup.get_basic_snapshot()
    assert snapshot.chat_type == ChatType.GROUP
    lp.sec("Send message to group to create it")
    dgroup.send_text("Hello, welcome to our group!")

    lp.sec("Waiting for reply")
    reply = delta.wait_for_incoming_msg().get_snapshot()
    assert reply.text == get_leave_msg()
    assert reply.quote
    assert reply.chat != dgroup
    delta.wait_for_incoming_msg()
    assert len(dgroup.get_contacts()) == 1

    assert not woot.get_contact(delta.get_config('addr'))
