function dB_to_IEC(dB) {
    if (dB < -70.0) {
        return 0.0;
    } else if (dB < -60.0) {
        return (dB + 70.0) * 0.0025;
    } else if (dB < -50.0) {
        return (dB + 60.0) * 0.005 + 0.025;
    } else if (dB < -40.0) {
        return (dB + 50.0) * 0.0075 + 0.075;
    } else if (dB < -30.0) {
        return (dB + 40.0) * 0.015 + 0.15;
    } else if (dB < -20.0) {
        return (dB + 30.0) * 0.02 + 0.3;
    } else {
        return (dB + 20.0) * 0.025 + 0.5;
    }
}