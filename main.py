import sys
sys.dont_write_bytecode = True

import medicine_minder_controller


if __name__ == '__main__':
    medicine_minder_controller.main(debug=False)
    print 'done'
