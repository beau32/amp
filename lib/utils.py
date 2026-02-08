"""Utility functions for date format conversion, ID validation, and hashing."""

import hashlib

# C# date format mappings to Python strftime format
FORMAT_CHANGES = (
    ('yyyy', '%Y'), ('yyy', '%Y'), ('yy', '%y'), ('y', '%y'),
    ('MMMM', '%B'), ('MMM', '%b'), ('MM', '%m'), ('M', '%m'),
    ('dddd', '%A'), ('ddd', '%a'), ('dd', '%d'), ('d', '%d'),
    ('HH', '%H'), ('H', '%H'), ('hh', '%I'), ('h', '%I'),
    ('mm', '%M'), ('m', '%M'),
    ('ss', '%S'), ('s', '%S'),
    ('tt', '%p'), ('t', '%p'),
    ('zzz', '%z'), ('zz', '%z'), ('z', '%z'),
)


def convert_csharp_date_format(input_format):
    """
    Convert C# date format string to Python strftime format.

    Args:
        input_format: C# date format string (e.g., 'yyyy-MM-dd')

    Returns:
        String formatted for Python's strftime function.
    """
    output = ""
    fmt = input_format

    while fmt:
        if fmt[0] == "'":
            # Literal text enclosed in single quotes
            apos = fmt.find("'", 1)
            if apos == -1:
                apos = len(fmt)
            output += fmt[1:apos].replace("%", "%%")
            fmt = fmt[apos + 1:]
        elif fmt[0] == "\\":
            # Escaped literal character
            output += fmt[1:2].replace("%", "%%")
            fmt = fmt[2:]
        else:
            # Match format tokens against known mappings
            for in_token, out_token in FORMAT_CHANGES:
                if fmt.startswith(in_token):
                    output += out_token
                    fmt = fmt[len(in_token):]
                    break
            else:
                # No match found - emit character as literal
                output += fmt[0].replace("%", "%%")
                fmt = fmt[1:]

    return output


def convert_salesforce_15_to_18(salesforce_id):
    """
    Convert a Salesforce 15-character ID to a 18-character ID.

    Salesforce IDs can be represented as either 15 characters (case-sensitive)
    or 18 characters (case-insensitive with checksum).

    Args:
        salesforce_id: 15-character Salesforce ID string

    Returns:
        18-character Salesforce ID string

    Raises:
        ValueError: If ID is not 15 characters long or is None
        TypeError: If ID is not a string
    """
    if not salesforce_id:
        raise ValueError("No id given.")
    if not isinstance(salesforce_id, str):
        raise TypeError("The given id isn't a string")
    if len(salesforce_id) == 18:
        return salesforce_id
    if len(salesforce_id) != 15:
        raise ValueError("The given id isn't 15 characters long.")

    # Generate three checksum characters based on case-sensitivity
    for i in range(0, 3):
        f = 0

        # Process each 5-character block
        for j in range(0, 5):
            # Get the character from the current 5-character block
            char = salesforce_id[i * 5 + j]

            # Check if character is uppercase letter
            if 'A' <= char <= 'Z':
                # Set bit j in the checksum
                f += 1 << j

        # Append the checksum character for this block
        salesforce_id += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'[f]

    return salesforce_id


def hash_string(algorithm, text):
    """
    Compute a hash digest of the given text using the specified algorithm.

    Args:
        algorithm: Hash algorithm name ('md5', 'sha1', 'sha256', etc.)
        text: String to hash

    Returns:
        Hexadecimal hash digest string
    """
    encoded_bytes = text.encode('utf-8')
    hash_obj = getattr(hashlib, algorithm)()
    hash_obj.update(encoded_bytes)
    return hash_obj.hexdigest()