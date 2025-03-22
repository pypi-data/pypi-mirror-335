import streamlit as st
import inspect


st.info("Pan Lit!")


lc, rc = st.columns(2)


emoji = '🦜↙🐎↙🪪↙🅿🎋'

emoji1 = '🦜🐎↙🪪🅿'
unicode_escape = emoji.encode('unicode-escape').decode('utf-8')
# st.write(unicode_escape)

# normal_string = 'U+1F40E'.encode('utf-8').decode('unicode-escape')
# st.write(normal_string)

# def convert_unicode_format(unicode_string):
#     numeric_part = unicode_string[2:]
#     integer_value = int(numeric_part)
#     hex_string = "{:04X}".format(integer_value)
#     return "U" + hex_string
#
# unicode_code_point = convert_unicode_format('U+1F40E')
# # unicode_character = chr(int(unicode_code_point, 16))
# unicode_character = unicode_code_point
# st.write(unicode_character)

with lc:
    x = st.slider(
    'Select a range of values',
    0, 100, 5)  # 👈 this is a widget
    bar = st.progress(0)
    bar.progress(int(x) + 1)

with rc:
    uc=emoji*x*2
    st.write(uc, x*2)
