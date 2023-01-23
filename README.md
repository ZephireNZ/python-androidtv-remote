# androidtv-remote

Library to interact with Google's AndroidTV Remote API v2.

Huge thanks to the below for the reverse engineering and example code:

- [Aymkdn/assistant-freebox-cloud](https://github.com/Aymkdn/assistant-freebox-cloud/wiki/Google-TV-(aka-Android-TV)-Remote-Control-(v2))
- [louis49/androidtv-remote](https://github.com/louis49/androidtv-remote)

## Pairing

To begin with, you'll need to have or generate an RSA private key with a public certificate.

Then, create an instance of the Pairing Manager

```python
pm = PairingManager(
    key_path="key.pem",
    cert_path="cert.pem",
    host="1.2.3.4"
)
```

Start the pairing process with `pm.start_pairing()` and then after requesting input from the user, pass this to `pm.send_secret(pin)`.

An exception `androidtv_remote.WrongPINError` will be thrown if the PIN is invalid, and a `SocketException` for errors due to network/pairing process itself.

## Remote Control

Once pairing is complete, create the remote manager:

```python
rm = RemoteManager(
    key_path="key.pem",
    cert_path="cert.pem",
    host="1.2.3.4",
    device_info=DeviceInfo(
        model="My Model",
        vendor="My Vendor",
        package_name="my.package.name",
        app_version="1.0.0"
    )
)
```

Then connect with `rm.connect()`.

The main loop runs with `rm.loop(callback)` - which waits for a message from the TV, and relays this to a callback. This includes events such as the TV turning on or off, volume change, opening an app, etc. The full list of message types can be found in the `remote.proto` file under `RemoteMessage`. Call `Message.HasField` to check the type of message.

Sending messages (eg for a key press) can be done via `rm.send` or via the helper methods on the manager. For example:

```python
def callback(msg: RemoteMessage):
    print(msg)

async def key_input():
    while True:
        inp = await ainput("Key: ")
        
        key = RemoteKeyCode.Value(inp)

        await rm.send_key(key, RemoteDirection.SHORT)
    
    rm.disconnect()

await rm.connect()

await asyncio.gather(
    rm.loop(callback),
    key_input(),
)
```