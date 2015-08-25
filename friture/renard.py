# Renard's numbers, or preferred numbers
# used for frequency display
# R5 for octave analyzer
# R10 for 1/3 octave analyzer
# R20 for 1/6 octave analyzer
# R40 for 1/12 octave analyzer
# R80 for 1/24 octave analyzer
# see http://en.wikipedia.org/wiki/Preferred_number

R5 = [1.00, 1.60, 2.50, 4.00, 6.30]

R10a = [1.25, 2.00, 3.15, 5.00, 8.00]

R10 = R5 + R10a
R10.sort()

R20a = [1.12, 1.40, 1.80, 2.24, 2.80, 3.55, 4.50, 5.60, 7.10, 9.00]
R20 = R10 + R20a
R20.sort()

R40a = ([1.06, 1.32, 1.70, 2.12, 2.65, 3.35, 4.25, 5.30, 6.70, 8.50]
        + [1.18, 1.50, 1.90, 2.36, 3.00, 3.75, 4.75, 6.00, 7.50, 9.50])
R40 = R20 + R40a
R40.sort()

R80a = ([1.03, 1.28, 1.65, 2.06, 2.58, 3.25, 4.12, 5.15, 6.50, 8.25]
        + [1.09, 1.36, 1.75, 2.18, 2.72, 3.45, 4.37, 5.45, 6.90, 8.75]
        + [1.15, 1.45, 1.85, 2.30, 2.90, 3.65, 4.62, 5.80, 7.30, 9.25]
        + [1.22, 1.55, 1.95, 2.43, 3.07, 3.87, 4.87, 6.15, 7.75, 9.75])
R80 = R40 + R80a
R80.sort()

if __name__ == "__main__":
    print("R5", R5)
    print()
    print("R10", R10)
    print()
    print("R20", R20)
    print()
    print("R40", R40)
    print()
    print("R80", R80)
