import { FunctionFactory } from "survey-core"
import Rand, { PRNG } from 'rand-seed';

function registerCustomFunctions() {
    FunctionFactory.Instance.register("round", round);
    FunctionFactory.Instance.register("random", random)
}

function round(params) {
    // round number to nearest multiple of second parameter
    // round(number | questionName | variableName, multiple)
    let num;
    if (typeof params[0] === 'number') {
        num = params[0];
    } else if (this.survey.getQuestionByName(params[0])?.value) {
        num = this.survey.getQuestionByName(params[0]).value;
    } else if (this.survey.getVariable(params[0])) {
        num = this.survey.getVariable(params[0]);
    }
    return Math.round((num + Number.EPSILON) * 10 * params[1]) / 10 * params[1];
}

function random(params) {
    // get random integer between min and max (inclusive)
    // random(min, max, seed)
    let min = params[0];
    let max = params[1];
    const seed = params[2] || Math.random();
    min = Math.ceil(min);
    max = Math.floor(max);
    const rand = new Rand(this.survey.participantID + seed);
    return Math.floor(rand.next() * (max - min + 1)) + min;
}

export default registerCustomFunctions;