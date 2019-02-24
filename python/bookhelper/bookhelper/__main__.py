import sys

def main():
    sys.path.extend(['..','.'])
    import bookhelper
    
    if len(sys.argv) > 1:
        sys.argv.insert(1,'-f')
        if len(sys.argv) > 3:
            sys.argv.insert(3, '-t')
    print('args:',sys.argv)
    bookhelper.doMain()


if __name__=="__main__":
    main()
