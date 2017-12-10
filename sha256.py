def sha256_algorithm(string_to_decode):
    ml = string_to_decode
    new_string = []
    bii = 0
    k = 0
    new_string = []
    bii = 0
    kCounter = 0
    new_length = 0
    appended2_length = 0
    appended2= 0
    schedule_array = []
    bii1 = 0
    zeroCounter = 0
    h0 = 0x6a09e667
    h1 = 0xbb67ae85
    h2 = 0x3c6ef372
    h3 = 0xa54ff53a
    h4 = 0x510e527f
    h5 = 0x9b05688c
    h6 = 0x1f83d9ab
    h7 = 0x5be0cd19

    k = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

    def right_rotate(number, order):
        lengthBit = 32
        if isinstance(number, str):
            new_number = int(number,2)
        else:
            new_number = number
        rightRotate = (new_number >> order) | (new_number<<lengthBit-order)
        return rightRotate%2**32
    def verify_string(variable_check):
        if isinstance(variable_check, str):
            to_return = int(variable_check,2)
        else:
            to_return = variable_check
        return to_return
        
    ##BREAK THE STRING INTO CHARACTERS
    for i in ml:
        asciCharacter = ord(i)
        charBinary = format(asciCharacter, '#010b')
##        print(charBinary)
        bii = (bii <<8) | (int(charBinary,2))
        if zeroCounter==0:
            bii1 = bii
        zeroCounter +=1
##    print(bin(bii))
##    print("hello")
##    print(bii.bit_length())
##    print(bii1.bit_length())
    if bii.bit_length()%8 != 0:
        appended2_length = 8-bii1.bit_length()
        new_length = bii.bit_length() + appended2_length
        
    else:
        new_length = bii.bit_length()
        appended2_length = 0
    appended = (bii<<1) | (1)
##    print(bin(appended))
    while((appended2.bit_length() + appended2_length)%512 != 448):
        kCounter+=1
        appended2 = appended<<kCounter

    representation = format(new_length, '#064b')
    ##print(representation )
    final_append = (appended2 <<64) | (int(representation,2))

    ##Prepend the last 0 to the final string
    final_string = format(final_append, 'b').zfill(final_append.bit_length() + appended2_length)
##    print(final_string)
    ##Defines how many chunks the string needs to be divided in
    chunks = int(len(final_string)/512)
##    print(chunks)
    for i in range(0, chunks):
        zi = 512*i
        word = []
        str_tr = int(512*(i+1))
        for j in range(zi,str_tr, 32):
            word.append(str(final_string[j:j+32]))
      
        for l in range(16,64):
            s0 = (right_rotate(word[l-15] , 7))  ^ (right_rotate(word[l-15], 18))  ^ ((verify_string(word[l-15])%2**32) >> 3)
            s1 = (right_rotate(word[l-2], 17))  ^ (right_rotate(word[l-2], 19))  ^ ((verify_string(word[l-2])%2**32) >> 10)
            word.append((verify_string(word[l-16]) + s0 + verify_string(word[l-7]) + s1)%2**32)
    ##    print(word)

        a = h0
        b = h1
        c = h2
        d = h3
        e = h4
        f = h5
        g = h6
        h = h7
     
        for m in range(0,64):
            S1 = (right_rotate(e,6))  ^ (right_rotate(e,11)) ^ (right_rotate(e,25))
            ch = (e & f) ^ ((~e) & g)
            temp1 = (h + S1 + ch + k[m] + verify_string(word[m]))%2**32
            S0 = (right_rotate(a,2)) ^ (right_rotate(a,13)) ^ (right_rotate(a,22))
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj)%2**32
            
            h = g
            g = f
            f = e
            e = (d + temp1)%2**32
            d = c
            c = b
            b = a
            a = (temp1 + temp2)%2**32


        h0 = (h0 + a)%2**32
        h1 = (h1 + b)%2**32
        h2 = (h2 + c)%2**32
        h3 = (h3 + d)%2**32
        h4 = (h4 + e)%2**32
        h5 = (h5 + f)%2**32
        h6 = (h6 + g)%2**32
        h7 = (h7 + h)%2**32
        
    s = (((hex(h0))[2:]).zfill(8),((hex(h1))[2:]).zfill(8),((hex(h2))[2:]).zfill(8),((hex(h3))[2:]).zfill(8),((hex(h4))[2:]).zfill(8),((hex(h5))[2:]).zfill(8),((hex(h6))[2:]).zfill(8),((hex(h7))[2:]).zfill(8))

    h_final = ''.join(s)
    return h_final      
