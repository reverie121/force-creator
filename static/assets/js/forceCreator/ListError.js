class ListError {
    constructor(type, message) {
        this.type = type;        // String identifier for the error type
        this.message = message;  // Human-readable error message
    }

    // Static method to check a ForceList instance and return an array of ListError objects
    static checkErrors(forceList) {
        const errors = [];

        // Error 1: Points over max
        if (forceList.totalForcePoints > forceList.maxPoints) {
            errors.push(new ListError(
                "points_over_max",
                `Total force points (${forceList.totalForcePoints}) exceed the maximum allowed (${forceList.maxPoints}).`
            ));
        }

        // Error 2: Too many support units (core:support ratio < 2:1)
        if (forceList.coreCount > 0 && forceList.supportCount > 0) {
            const ratio = forceList.coreCount / forceList.supportCount;
            if (ratio < 2) {
                errors.push(new ListError(
                    "too_many_support_units",
                    `Too many support units: ${forceList.supportCount} support units exceed the 2:1 core-to-support ratio (core units: ${forceList.coreCount}).`
                ));
            }
        } else if (forceList.supportCount > 0 && forceList.coreCount === 0) {
            errors.push(new ListError(
                "too_many_support_units",
                `Support units (${forceList.supportCount}) present with no core units, violating the 2:1 core-to-support ratio.`
            ));
        }

        // Error 3: Standard Commander too many special rules
        if (forceList.commander && forceList.commander.commanderclass_id === 1) { // Standard Commander
            const maxSpecialRules = forceList.commander.name.startsWith('Seasoned') ? 2 : 1;
            const selectedSpecialRules = forceList.commander.specialruleChosenIDs 
                ? forceList.commander.specialruleChosenIDs.length 
                : 0;
            if (selectedSpecialRules > maxSpecialRules) {
                errors.push(new ListError(
                    "standard_commander_too_many_special_rules",
                    `Standard Commander "${forceList.commander.nickname}" has too many special rules selected (${selectedSpecialRules}) - maximum allowed is ${maxSpecialRules}.`
                ));
            }
        }

        return errors;
    }

    // Method to get a string representation of the error
    toString() {
        return `${this.type}: ${this.message}`;
    }
}