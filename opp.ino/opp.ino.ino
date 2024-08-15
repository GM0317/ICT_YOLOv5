#include <Servo.h>

Servo myServo;  // 서보 모터 객체 생성
int servoPin = 8;  // 서보 모터 핀 번호 설정 (예: 핀 8)
bool isLocked = false;  // 현재 서보의 상태를 저장하는 변수
int ledPin = LED_BUILTIN;  // 내장된 LED 핀 번호 설정

void setup() {
    myServo.attach(servoPin);  // 서보 모터를 제어할 핀에 연결
    myServo.write(0);  // 초기 위치로 설정
    pinMode(ledPin, OUTPUT);  // LED 핀을 출력으로 설정
    Serial.begin(9600);
}

void loop() {
    
    // Serial 통신을 통해 들어오는 명령을 확인
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        if (command == "LOCK" && !isLocked) {
            Serial.print("on");
            myServo.write(90);  // 서보 모터를 90도로 회전
            isLocked = true;
        } else if (command == "UNLOCK" && isLocked) {
            Serial.print("off");
            myServo.write(0);  // 서보 모터를 0도로 되돌림
            isLocked = false;
            digitalWrite(ledPin, LOW);  // UNLOCK 상태일 때 LED 끄기
        }
    }

    // LOCK 상태일 때 LED 깜빡이기
    if (isLocked) {
        digitalWrite(ledPin, HIGH);  // LED 켜기
        delay(500);  // 0.5초 대기
        digitalWrite(ledPin, LOW);  // LED 끄기
        delay(500);  // 0.5초 대기
    }
}
