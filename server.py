
def homepage():
    with open('./abc111.txt', 'w') as f:
        f.write("aaaaabbbbbbbbbbbbbb0")
    return "helllllllo   word"


if __name__ == "__main__":
    print(homepage())
