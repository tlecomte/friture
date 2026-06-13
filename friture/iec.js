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
        return Math.min(1.0, (dB + 20.0) * 0.025 + 0.5);
    }
}

function normalizeUnitLabel(unitLabel) {
    if (unitLabel === "dBFS" || unitLabel === "dB") {
        return "dB FS";
    }
    return unitLabel;
}

function meterDisplayRange(unitLabel) {
    var normalized = normalizeUnitLabel(unitLabel);
    if (normalized === "dBSPL") {
        return { bottom: 40.0, top: 120.0 };
    }
    if (normalized === "dBu") {
        return { bottom: -40.0, top: 20.0 };
    }
    return null;
}

function meterScaleTicks(unitLabel) {
    var range = meterDisplayRange(unitLabel);
    if (range === null) {
        return [0, -3, -6, -10, -20, -30, -40, -50, -60];
    }
    var ticks = [];
    for (var tick = range.top; tick >= range.bottom; tick -= 10.0) {
        ticks.push(tick);
    }
    return ticks;
}

function level_db_to_meter_fraction(levelDb, unitLabel) {
    var range = meterDisplayRange(unitLabel);
    if (range === null) {
        return dB_to_IEC(Math.min(levelDb, 0.0));
    }
    if (levelDb <= range.bottom) {
        return 0.0;
    }
    if (levelDb >= range.top) {
        return 1.0;
    }
    return (levelDb - range.bottom) / (range.top - range.bottom);
}

function level_db_to_iec(levelDb, unitLabel) {
    return level_db_to_meter_fraction(levelDb, unitLabel);
}
