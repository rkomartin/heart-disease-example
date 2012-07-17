import heart_disease.run
import random
import veritable

API = veritable.connect()


def test_example():
    heart_disease.run.TABLE_ID = 'heart-disease-example_'+str(random.randint(0, 100000000))
    heart_disease.run.main()
    API.delete_table(heart_disease.run.TABLE_ID)
    API.delete_table(heart_disease.run.TABLE_ID+"-binary")



