"""
A function that checks the strength of a password provided

@param password: a string of password to be evaluated
@return: a string indicateds the password strength
"""
import string
def password_strength(password):
    # initial password strength
    strength = 0

    # increase strength value if password match the condition below
    if len(password) >= 12:
        strength += 1
    
    for i in password:
        if i.islower():
            strength += 1
            break
    
    for i in password:
        if i.isupper():
            strength += 1
            break

    for i in password:
        if i.isdigit():
            strength += 1
            break
    
    for i in password:
        if i in string.punctuation:
            strength += 1
            break

    # return the password strength
    if strength == 5:
        return "\tStrong password! 💪"
    elif strength >= 3:
        return "\tModerate password. 🔒"
    else:
        return "\tWeak password. 🚨"
