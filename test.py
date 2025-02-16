import warawara

yn = warawara.prompt('Do you like warawara, or do you not like it?', ('yes', 'no'))
print("You've replied:", yn)

assert yn == 'yes'
assert yn == 'Yes'
assert yn == 'YES'
assert yn == ''
assert yn != 'no'

assert yn.selected == ''
