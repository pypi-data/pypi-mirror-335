"""
The following example shows how to update the object to run on
new parameters.
It is generally not recommended to use this if there is a better way,
for example if you want to change the message, it's better to just create
a new message object, however the only way to update SQL manager for logging is via the
update method.
"""
from datetime import timedelta
import asyncio
import daf


message = daf.TextMESSAGE(
    data=daf.TextMessageData("Hello"),
    channels=[123455, 1425215],
    period=daf.FixedDurationPeriod(timedelta(seconds=5))
)

accounts = [
    daf.ACCOUNT(
        token="SKJDSKAJDKSJDKLAJSKJKJKGSAKGJLKSJG",
        is_user=False,
        servers=[
            daf.GUILD(1234567, [message])
        ]
    )
]


async def user_task():
    # Will send "Hello" every 5 seconds
    await asyncio.sleep(10)
    await message.update(
        period=daf.FixedDurationPeriod(timedelta(seconds=20)),
    )
    # Will send "Hello" every 20 seconds

if __name__ == "__main__":
    daf.run(user_callback=user_task, accounts=accounts)  
