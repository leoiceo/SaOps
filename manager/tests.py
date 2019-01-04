from django.test import TestCase

# Create your tests here.

from tasks import add
if __name__ == '__main__':
    for i in range(100):
        for j in range(100):
            add.delay(i, j)
