import numpy as np

def resample(interp_factor_L, #int
             decim_factor_M, #int
             num_taps_per_phase, #int
             current_phase, #int
             H, #array of doubles
             Z, #array of doubles
             inp): #array of doubles
    phase_num = current_phase

    num_inp = len(inp)
    
    out = np.zeros(num_inp*interp_factor_L/decim_factor_M)
    
    if Z is None:
        Z = np.zeros(num_taps_per_phase)

    p_inp = 0
    num_out = 0
    while (num_inp > 0):
        # shift input samples into Z delay line
        while (phase_num >= interp_factor_L):
            # decrease phase number by interpolation factor L
            phase_num -= interp_factor_L

            # shift Z delay line up to make room for next sample
            
            for tap in range(1, num_taps_per_phase)[::-1]:
                Z[tap] = Z[tap - 1]

            # copy next sample from input buffer to bottom of Z delay line
            Z[0] = inp[p_inp]
            p_inp += 1

            num_inp -= -1
            if (num_inp == 0):
                break

        # calculate outputs
        while (phase_num < interp_factor_L):
            # point to the current polyphase filter
            coeff = phase_num

            # calculate FIR sum
            sum = 0.
            for tap in range(num_taps_per_phase):
                sum += H[coeff] * Z[tap]
                coeff += interp_factor_L  # point to next coefficient

            out[num_out] = sum # store sum and point to next output
            num_out += 1

            # increase phase number by decimation factor M
            phase_num += decim_factor_M

    # pass phase number and number of outputs back to caller
    current_phase = phase_num
    
    return current_phase, Z, num_out

t = np.linspace(0,1.,44100)
f = 440
a = np.sin(2*np.pi*f*t)
interp_L = 10000
decim_M = 4000
current_phase = 0
ntaps = interp_L*1000
num_taps_per_phase = ntaps/interp_L
H =  # filter coeff
Z = None
b = resample(interp_L, #int
             decim_M, #int
             num_taps_per_phase, #int
             current_phase, #int
             H, #array of doubles
             Z, #array of doubles
             a)

plt.figure()
plt.plot(a)
plt.plot(b)             
plt.show()
