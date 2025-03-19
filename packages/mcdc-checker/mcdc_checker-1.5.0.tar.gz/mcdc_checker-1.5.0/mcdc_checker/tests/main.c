/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

int if_else(int a, int b, int c) {
    if ((a && b) || c) {
        return 5;
    } else {
        return 10;
    }
}

int if_else_tree(int a, int b, int c) {
    if (c || (a && b)) {
        return 5;
    } else {
        return 10;
    }
}

int if_else_simple(int a, int b, int c) {
    if (a && b) {
        return 5;
    } else if(c) {
        return 5;
    } else {
        return 10;
    }
}

int if_else_comparison(int a, int b, int c) {
    if (a > 5 && b < 3) {
        return 5;
    } else if(c == 4) {
        return 5;
    } else {
        return 10;
    }
}

#include "test.h"

int return_logical(int a, int b, int c) {
    return ((a && b) || c) ? 5 : 10;
}

int return_logical2(int a, int b, int c) {
    return (a && b) || c;
}

int return_bitwise(int a, int b, int c) {
    return (a & b) | c;
}

int return_arith(int a, int b, int c) {
    return (a * b) + c;
}

void variable_assignment(int a, int b, int c) {
    int result = (a && b) || c;
}

int compare_vars(int a, double b, int c) {
    return ((a < b || c > 4 || b < 2.5) && b < c);
}

int conditional_operator(int a, int b, int c) {
    return ((a && c) || b) ? c : 3;
}

int worst_case(int a, int b, int c) {
    return (a == (b || c) && b < 3);
}

int non_correctable(int a, int b, int c, int d, int e) {
    return (a && b || c && d || e);
}

int main() {
    if_else(1,2,3);
    if_else_tree(1,2,3);
    if_else_simple(1,2,3);
    return_logical(1,2,3);
    return_logical2(1,2,3);
    return_bitwise(1,2,3);
    return_arith(1,2,3);
    variable_assignment(1,2,3);
    compare_vars(1,2,3);
    worst_case(1,2,3);
    non_correctable(1,2,3,4,5);
}
