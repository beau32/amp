import hashlib

_format_changes = (
    ('yyyy', '%Y'), ('yyy', '%Y'), ('yy', '%y'),('y', '%y'),
    ('MMMM', '%B'), ('MMM', '%b'), ('MM', '%m'),('M', '%m'),
    ('dddd', '%A'), ('ddd', '%a'), ('dd', '%d'),('d', '%d'),
    ('HH', '%H'), ('H', '%H'), ('hh', '%I'), ('h', '%I'),
    ('mm', '%M'), ('m', '%M'),
    ('ss', '%S'), ('s', '%S'),
    ('tt', '%p'), ('t', '%p'),
    ('zzz', '%z'), ('zz', '%z'), ('z', '%z'),
    )

def cnv_csharp_date_fmt(in_fmt):
    ofmt = ""
    fmt = in_fmt
    while fmt:
        if fmt[0] == "'":
            # literal text enclosed in ''
            apos = fmt.find("'", 1)
            if apos == -1:
                # Input format is broken.
                apos = len(fmt)
            ofmt += fmt[1:apos].replace("%", "%%")
            fmt = fmt[apos+1:]
        elif fmt[0] == "\\":
            # One escaped literal character.
            # Note graceful behaviour when \ is the last character.
            ofmt += fmt[1:2].replace("%", "%%")
            fmt = fmt[2:]
        else:
            # This loop could be done with a regex "(yyyy)|(yyy)|etc".
            for intok, outtok in _format_changes:
                if fmt.startswith(intok):
                    ofmt += outtok
                    fmt = fmt[len(intok):]
                    break
            else:
                # Hmmmm, what does C# do here?
                # What do *you* want to do here?
                # I'll just emit one character as literal text
                # and carry on. Alternative: raise an exception.
                ofmt += fmt[0].replace("%", "%%")
                fmt = fmt[1:]
    return ofmt

def sf15to18 (id):
	if not id:
		raise ValueError('No id given.')
	if not isinstance(id, str):
		raise TypeError('The given id isn\'t a string')
	if len(id) == 18:
		return id
	if len(id) != 15:
		raise ValueError('The given id isn\'t 15 characters long.')

	# Generate three last digits of the id
	for i in range(0,3):
		f = 0

		# For every 5-digit block of the given id
		for j in range(0,5):
			# Assign the j-th chracter of the i-th 5-digit block to c
			c = id[i * 5 + j]

			# Check if c is an uppercase letter
			if c >= 'A' and c <= 'Z':
				# Set a 1 at the character's position in the reversed segment
				f += 1 << j

		# Add the calculated character for the current block to the id
		id += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'[f]

	return id

def decrypt(name,str):
    encoded_string = str.encode('utf-8')

    # Create a SHA-256 hash object
    hash = getattr(hashlib,name)()

    # Update the hash object with the encoded bytes
    hash.update(encoded_string)

    # Get the hexadecimal representation of the hash
    hashed_string = hash.hexdigest()

    return hashed_string