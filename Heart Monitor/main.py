# This program simulates the controller of a heart monitoring device.
# It reads the pulse, the oxygen level as well as the blood pressure.
# Its main purpose is to raise alarms if there is something seriously wrong.

import sys

MAX_ZEROES_IN_ROW_TO_BREAK = 5

PULSE_EXTREME = 300
OXYGEN_EXTREME = 100
BLOOD_PRESSURE_EXTREME = (370, 360)

STOP_STRS = ["q", "quit"]
FIXED_STR = "fixed"

SENSOR_BROKEN_MESSAGE = "Critical Warning! The sensor seems to be broken." \
                        " Type 'fixed' after after fixing it to continue monitoring."


def print_out(out, text):
    out.write(text)
    out.write("\n")
    out.flush()


def check_pulse(number, out=sys.stdout):

    # normal heart rate
    if (number >= 60 and number <= 100):
        print_out(out, "Heart rate is normal.")
    
    # low heart rate
    elif (number >= 40 and number <= 59):
        print_out(out, "Heart rate is low, but it can be normal for active individuals.")
    
    # low heart rate
    elif (number <= 39):
        print_out(out, "WARNING! Heart rate is low. Seek medical attention!")
    
    # increasing heart rate
    elif (number >= 101 and number <= 120):
        print_out(out, "WARNING! Heart rates have increased. Seek medical attention!")
    
    # heart rate increasing too high
    elif (number > 120 and number <= 140):
        print_out(out, "WARNING! Heart rate is high. Seek medical attention!")
    
    # critically high
    elif number > 140:
        print_out(out, "Warning! The situation is critical!! The heart rate is extremely high! Seek medical attention!")

        
def check_blood_pressure(blood_pressure, out=sys.stdout):
    first, second = blood_pressure
    
    # low bloodpressure
    if first <= 90 and second <= 60:
        print_out(out, "WARNING! Low blood pressure! seek medical attention!")

    # prehypertension between 120/80 and 140/90
    elif first > 120 and first < 140 and second > 80 and second < 90:
        print_out(out, "WARNING! Prehypertension! Seek medical attention!")
    
    # high blood pressure over 140/90
    elif first >= 140 and second >= 90:
        print_out(out, "WARNING! High blood pressure! Seek medical attention!")

    # high first number and normal second number
    elif first >= 140 and second >= 60 and second <= 90 :
        print_out(out, "Isolated systolic hypertension! Normal for older people, but further tests should be performed.")
    
    # normal first number and high second number
    elif first > 90 and first < 140 and second < 60:
        print_out(out, "Isolated diastolic blood pressure! Seek medical attention.")
    
    # normal bloodpressure
    elif first >= 90 and first <= 120 and second >= 60 and second <= 80 :
        print_out(out, "Blood pressure is normal.")
    
    else:
        print_out(out, "We shouldnt be able to get to here")
    
    # check difference between systolic and diastolic
    if first - second > 60:
        print_out(out, "WARNING! Wide pulse pressure! Seek medical attention!")
    pass


def check_oxygen(number, out=sys.stdout):

    # normal oxygen level
    if number >= 95:
        print_out(out, "Oxygen level is normal.")
    
    # low oxygen level
    elif (number < 95 and number >= 85):
        print_out(out, "WARNING! Not enough Oxygen in blood!")
    
    # very low oxygen level
    else:
        print_out(out, "WARNING! Situation is very critical. Oxygen in body is NOT ENOUGH!!!")


def check_for_correctness(split_values):
    if len(split_values) != 3:
        return False

    pulse, oxygen, blood_pressure = split_values

    if not (str.isnumeric(pulse) and str.isnumeric(oxygen)):
        return False

    split_blood = blood_pressure.split("/")
    if len(split_blood) != 2 or not (str.isnumeric(split_blood[0]) and str.isnumeric(split_blood[1])):
        return False

    return True


def get_numeric_values(split_values):
    pulse, oxygen, blood_pressure = split_values
    pulse, oxygen = int(pulse), int(oxygen)

    split_blood = blood_pressure.split("/")
    blood_pressure = (int(split_blood[0]), int(split_blood[1]))

    return pulse, oxygen, blood_pressure


def check_zeroes(zeroes_in_row, pulse, oxygen, blood_pressure):
    if pulse == 0:
        zeroes_in_row[0] += 1
    else:
        zeroes_in_row[0] = 0

    if oxygen == 0:
        zeroes_in_row[1] += 1
    else:
        zeroes_in_row[1] = 0

    if blood_pressure[0] == 0:
        zeroes_in_row[2] += 1
    else:
        zeroes_in_row[2] = 0

    if blood_pressure[1] == 0:
        zeroes_in_row[3] += 1
    else:
        zeroes_in_row[3] = 0

    if max(zeroes_in_row) == MAX_ZEROES_IN_ROW_TO_BREAK:
        return [0, 0, 0, 0], False
    else:
        return zeroes_in_row, True


def check_extreme_values(pulse, oxygen, blood_pressure):
    if pulse > PULSE_EXTREME or oxygen > OXYGEN_EXTREME:
        return False

    if blood_pressure[0] > BLOOD_PRESSURE_EXTREME[0] or blood_pressure[1] > BLOOD_PRESSURE_EXTREME[1]:
        return False

    # Don't want to add another function specially for this
    if blood_pressure[0] <= blood_pressure[1]:
        return False

    return True


def run_reading_loop(inp, out):
    awaiting_fixing_mode = False
    zeroes_in_row = [0, 0, 0, 0]

    while True:
        print("\nPlease input the values for heart rate, oxygen and blood pressure. (e.g. 70 95 120/80)")
        line = inp.readline()
        split = line.split()

        if not line:
            break
        if len(split) == 1 and split[0] in STOP_STRS:
            break

        if awaiting_fixing_mode:
            if len(split) == 1 and split[0] == FIXED_STR:
                awaiting_fixing_mode = False
                zeroes_in_row = [0, 0, 0, 0]
            else:
                print_out(out, SENSOR_BROKEN_MESSAGE)
            continue

        if not check_for_correctness(split):
            awaiting_fixing_mode = True
            print_out(out, SENSOR_BROKEN_MESSAGE)
            continue

        pulse, oxygen, blood_pressure = get_numeric_values(split)

        zeroes_in_row, sensor_alright = check_zeroes(zeroes_in_row, pulse, oxygen, blood_pressure)
        if not sensor_alright:
            awaiting_fixing_mode = True
            print_out(out, SENSOR_BROKEN_MESSAGE)
            continue

        if not check_extreme_values(pulse, oxygen, blood_pressure):
            awaiting_fixing_mode = True
            print_out(out, SENSOR_BROKEN_MESSAGE)
            continue

        check_pulse(pulse, out)
        check_oxygen(oxygen, out)
        check_blood_pressure(blood_pressure, out)


def ask_input():
    print()
    print("In order to exit the program type q or quit")
    print()

    stop = ["q", "quit"]
    
    pulse = input("Enter heart rate per minute, (e.g. 70): ")
    if pulse.lower() in stop:
        return False

    if not (pulse.isnumeric()):
        while not(pulse.isnumeric()):
            print("The pulse number should be a positive integer number.")
            pulse = input("Enter heart rate per minute, (e.g. 70): ")
    
    if pulse.isnumeric():
        pulse = int(pulse)

    o2 = ""
    while not(o2.isnumeric()):
        o2 = input("Enter Oxygen level in percentages (e.g. 96): ")
        
        if o2.lower() in stop:
            return False

        if o2.isnumeric():
            o2int = int(o2)
            if o2int > 100:
                o2 = ""
                print("The oxygen number should be a positive integer number equal or smaller than 100.")
        else:
            print("The oxygen number should be a positive integer number equal or smaller than 100.")

    o2 = int(o2)

    blood_p = ""
    while not(blood_p.__contains__("/")):
        blood_p = input("Enter blood pressure (e.g. 120/80): ")

        if blood_p.lower() in stop:
            return False

        if blood_p.__contains__("/"):
            numbers = blood_p.split("/")
            first = numbers[0]
            second = numbers[1]

            if first.isnumeric() and second.isnumeric():
                first = int(first)
                second = int(second)
                if first <= second or first < 0 or second < 0:
                    blood_p = ""
                    print("The systolic blood pressure has to be higher than the diastolic blood pressure")
            else:
                blood_p = ""
                print("The blood pressure should be positive numbers")
        else:
            print("The blood pressure should be entered as two positive numbers with a dash '/' between them. e.g. 120/80")
    numbers = blood_p.split("/")
    blood_p = (int(numbers[0]), int(numbers[1]))
    print()

    check_pulse(pulse)

    check_oxygen(o2)

    check_blood_pressure(blood_p)

    print()
    return True


def main():
    mode = ""
    while True:
        mode = input("Enter program mode (console or file): ")
        if mode == "console" or mode == "file":
            break

    if mode == "console":
        inp = sys.stdin
        out = sys.stdout

        run_reading_loop(inp, out)
    else:
        names = ""
        while True:
            names = input("Enter input file name or both input and output file names: ")
            if len(names.split()) > 0:
                break

        split = names.split()
        with open(split[0], 'r') as inp:
            if len(split) > 1:
                with open(split[1], 'w') as out:
                    run_reading_loop(inp, out)
            else:
                out = sys.stdout
                run_reading_loop(inp, out)

    # while ask_input():
    #     pass


if __name__ == '__main__':
    main()
