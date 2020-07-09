for line in ll.get():
    comment = line.get('comment', '')
    if 'broadlink' not in comment:
        continue

    comment = comment[10:]
    comment = comment[0:1].upper() + comment[1:].replace(' room', ' Room')
    print(f"  - platform: broadlink\n    host: {line['address']}\n    mac: {line['mac-address']}\n    name: {comment}")

for line in ll.get():
    comment = line.get('comment', '')
    if 'yee' not in comment:
        continue

    comment = comment[9:]
    comment = comment[0:1].upper() + comment[1:].replace(' room', ' Room')
    print(f"    {line['address']}:\n      name: {comment}")
