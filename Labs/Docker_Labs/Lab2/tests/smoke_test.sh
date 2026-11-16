#!/usr/bin/env bash
# Smoke test for the running Iris container.
# usage: ./tests/smoke_test.sh [BASE_URL]   (default http://localhost:8080)
BASE=${1:-http://localhost:8080}
pass=0; fail=0

check() {  # check NAME EXPECTED ACTUAL
    if [[ "$3" == *"$2"* ]]; then
        echo "PASS  $1"; pass=$((pass + 1))
    else
        echo "FAIL  $1 (expected '$2', got '$3')"; fail=$((fail + 1))
    fi
}

echo "Testing $BASE"
check "GET /"         "Welcome to the Iris Classifier API" "$(curl -s "$BASE/")"
check "GET /health"   '"status":"ok"'                      "$(curl -s "$BASE/health" | tr -d ' \n')"
check "GET /predict"  "NEURAL IRIS"                        "$(curl -s "$BASE/predict")"

# Known samples from the Iris dataset: sepal_length sepal_width petal_length petal_width expected
while read -r sl sw pl pw expected; do
    out=$(curl -s -X POST "$BASE/predict" -d sepal_length=$sl -d sepal_width=$sw -d petal_length=$pl -d petal_width=$pw | tr -d ' \n')
    check "predict $sl,$sw,$pl,$pw -> $expected  $out" "\"predicted_class\":\"$expected\"" "$out"
done <<'EOF'
5.1 3.5 1.4 0.2 Setosa
5.0 3.4 1.5 0.2 Setosa
5.9 3.0 4.2 1.5 Versicolor
6.4 3.2 4.5 1.5 Versicolor
6.7 3.0 5.2 2.3 Virginica
6.3 3.3 6.0 2.5 Virginica
EOF

# JSON body works as well as the HTML form
out=$(curl -s -X POST "$BASE/predict" -H 'Content-Type: application/json' \
      -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}' | tr -d ' \n')
check "JSON body -> Setosa" '"predicted_class":"Setosa"' "$out"

# Bad input returns HTTP 400 with a clear message
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/predict" -d sepal_length=5.1)
check "missing fields -> 400" "400" "$code"
out=$(curl -s -X POST "$BASE/predict" -d sepal_length=abc -d sepal_width=3 -d petal_length=1 -d petal_width=0.2)
check "non-number -> error message" "must be a number" "$out"
out=$(curl -s -X POST "$BASE/predict" -d sepal_length=-5 -d sepal_width=3 -d petal_length=1 -d petal_width=0.2)
check "negative value -> error message" "between 0 and 30" "$out"

echo "----"
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
