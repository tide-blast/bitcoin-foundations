# Raw Bitcoin transaction decoder (legacy / non-segwit only, for now)

def hex_to_value_LEndian(string_hex):
    reversed_bytes = bytes.fromhex(string_hex)[::-1]  # Reversed values but still in byte objects (not text)
    reversed_bytes_hex = reversed_bytes.hex()          # Converts byte objects back into hex characters
    string_value = int(reversed_bytes_hex, 16)
    return string_value


def reverse_hex_bytes(string_hex):
    reversed_bytes = bytes.fromhex(string_hex)[::-1]
    reversed_bytes_hex = reversed_bytes.hex()
    return reversed_bytes_hex


def parse_compactsize(string_hex, offset):
    first_byte_hex = string_hex[offset:offset+2]
    first_byte_value = int(first_byte_hex, 16)
    if first_byte_value <= 252:
        number_value = first_byte_value
        offset = offset + 2
        return number_value, offset

    elif first_byte_value == 253:
        number_hex = string_hex[offset+2:offset+6]
        number_value = hex_to_value_LEndian(number_hex)
        offset = offset + 6
        return number_value, offset

    elif first_byte_value == 254:
        number_hex = string_hex[offset+2:offset+10]
        number_value = hex_to_value_LEndian(number_hex)
        offset = offset + 10
        return number_value, offset

    else:
        # first_byte_value is a single byte (0-255), so once we've ruled out
        # 252 and below, 253, and 254, 255 is the only remaining possibility
        number_hex = string_hex[offset+2:offset+18]
        number_value = hex_to_value_LEndian(number_hex)
        offset = offset + 18
        return number_value, offset


def parse_version(string_hex, offset):
    version_hex = string_hex[offset:offset+8]
    version_value = hex_to_value_LEndian(version_hex)
    offset = offset + 8
    return version_value, offset


def parse_inputs(string_hex, offset, input_count):
    inputs_list = []

    for i in range(input_count):
        input_txid_hex = reverse_hex_bytes(string_hex[offset:offset+64])
        offset = offset + 64

        input_number = hex_to_value_LEndian(string_hex[offset:offset+8])
        offset = offset + 8

        # parse_compactsize returns the length in bytes, not character count
        signature_length_bytes, offset = parse_compactsize(string_hex, offset)
        signature_value_hex = string_hex[offset:offset+signature_length_bytes*2]
        offset = offset + signature_length_bytes*2

        sequence = hex_to_value_LEndian(string_hex[offset:offset+8])
        offset = offset + 8

        input_dict = {"txid": input_txid_hex, "vout": input_number,
                      "scriptSig": signature_value_hex, "sequence": sequence}
        inputs_list.append(input_dict)

    return inputs_list, offset


def output_value(string_hex, offset, number_value):
    outputs_list = []

    for i in range(number_value):
        satoshis_int = hex_to_value_LEndian(string_hex[offset:offset+16])  # 8-byte integer
        offset = offset + 16

        scriptPubKey_length_bytes, offset = parse_compactsize(string_hex, offset)
        scriptPubKey_value_hex = string_hex[offset:offset+scriptPubKey_length_bytes*2]
        offset = offset + scriptPubKey_length_bytes*2

        output_dict = {"value": satoshis_int, "scriptPubKey": scriptPubKey_value_hex}
        outputs_list.append(output_dict)

    return outputs_list, offset


def parse_locktime(string_hex, offset):
    locktime_hex = string_hex[offset:offset+8]
    offset = offset + 8
    locktime_value = hex_to_value_LEndian(locktime_hex)
    return locktime_value, offset


def decode_transaction(string_hex):
    offset = 0

    version, offset = parse_version(string_hex, offset)

    input_count, offset = parse_compactsize(string_hex, offset)
    inputs_list, offset = parse_inputs(string_hex, offset, input_count)

    output_count, offset = parse_compactsize(string_hex, offset)
    outputs_list, offset = output_value(string_hex, offset, output_count)

    locktime, offset = parse_locktime(string_hex, offset)

    transaction_dict = {"Version": version, "TX Inputs": inputs_list,
                        "TX Outputs": outputs_list, "Locktime": locktime}
    return transaction_dict


def print_transaction(transaction_dict):
    print(f"Version: {transaction_dict['Version']}")
    print()

    print("Inputs:")
    for tx_input in transaction_dict["TX Inputs"]:
        print(f"  txid: {tx_input['txid']}")
        print(f"  vout: {tx_input['vout']}")
        print(f"  scriptSig: {tx_input['scriptSig']}")
        print(f"  sequence: {tx_input['sequence']}")
        print()

    print("Outputs:")
    for tx_output in transaction_dict["TX Outputs"]:
        print(f"  value (satoshis): {tx_output['value']}")
        print(f"  scriptPubKey: {tx_output['scriptPubKey']}")
        print()

    print(f"Locktime: {transaction_dict['Locktime']}")


if __name__ == "__main__":
    # Constructed legacy test transaction: version 2, 1 input, 1 output, locktime 933065
    test_hex = (
        "02000000"                      # version
        "01"                            # input count
        + "aa" * 32 + "00000000"        # txid + vout
        + "01" + "ab"                   # scriptSig length + scriptSig
        + "ffffffff"                    # sequence
        + "01"                          # output count
        + "0008af2f00000000"            # value
        + "01" + "cd"                   # scriptPubKey length + scriptPubKey
        + "c93c0e00"                    # locktime
    )
    result = decode_transaction(test_hex)
    print(result)
    print()
    print_transaction(result)