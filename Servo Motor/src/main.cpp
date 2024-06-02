#include <ESP32Servo.h>
#include <WiFi.h>
#include <HTTPClient.h>

// WiFi配置
const char* ssid = "Jase";
const char* password = "Jase123456";

// Firebase URL
const char* firebase_url = "https://pawsitude-2bab7-default-rtdb.firebaseio.com/predictions/prediction.json";
const char* firebase_url1 = "https://pawsitude-2bab7-default-rtdb.firebaseio.com/Barking/count.json";

// 定义舵机引脚
int servoPins[] = {1, 2, 3}; // 连接舵机的GPIO引脚
Servo servos[3]; // 创建舵机对象数组

int previousCount = -1; // 保存之前的count值
String previousStage = ""; // 保存之前的stage值

// 函数原型声明
void controlServos(String stage);
void handleCount(String count);
void moveServosActive();
void moveServosStress();
void moveServosBarking();

void setup() {
  Serial.begin(115200); // 启动串口通信

  // 连接WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // 初始化舵机
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  for (int i = 0; i < 3; i++) {
    servos[i].setPeriodHertz(50); // 标准50hz舵机
    servos[i].attach(servoPins[i], 500, 2400); // 设置PWM范围
  }
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // 获取第一个URL的数据
    http.begin(firebase_url);
    int httpResponseCode = http.GET();

    if (httpResponseCode == 200) {
      String payload = http.getString();
      Serial.println("Stage: " + payload);
      payload.trim();
      payload.replace("\"", ""); // 去掉字符串中的引号

      if (payload != previousStage) {
        previousStage = payload;
        controlServos(payload); // 从Firebase响应中提取stage数据并控制舵机
      }
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();

    // 获取第二个URL的数据
    http.begin(firebase_url1);
    httpResponseCode = http.GET();

    if (httpResponseCode == 200) {
      String payload1 = http.getString();
      Serial.print("Count: ");
      Serial.println(payload1);
      handleCount(payload1); // 处理count数据
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  }

  delay(1000); // 每1秒获取一次数据
}

void controlServos(String stage) {
  if (stage == "active") {
    moveServosActive();
  } else if (stage == "stress") {
    moveServosStress();
  } else if (stage == "barking") {
    moveServosBarking();
  } else {
    Serial.println("Unknown stage");
  }
}

void moveServosActive() {
  unsigned long startTime = millis();
  while (millis() - startTime < 6000) { // 运行6秒
    static int angle1 = 60;
    static int angle2 = 95;
    static int angle3 = 45;
    static bool increasing1 = true;
    static bool increasing2 = true;
    static bool increasing3 = false;

    // 控制第一个舵机 (一直动)
    if (increasing1) {
      angle1++;
      if (angle1 >= 180) {
        increasing1 = false;
      }
    } else {
      angle1--;
      if (angle1 <= 60) {
        increasing1 = true;
      }
    }
    servos[0].write(angle1);
    delay(15);

    // 控制第二和第三个舵机 (同时动)
    if (increasing2) {
      angle2++;
      if (angle2 >= 140) {
        increasing2 = false;
      }
    } else {
      angle2--;
      if (angle2 <= 95) {
        increasing2 = true;
      }
    }
    servos[1].write(angle2);

    if (increasing3) {
      angle3++;
      if (angle3 >= 45) {
        increasing3 = false;
      }
    } else {
      angle3--;
      if (angle3 <= 0) {
        increasing3 = true;
      }
    }
    servos[2].write(angle3);

    delay(20);
  }
}

void moveServosStress() {
  unsigned long startTime = millis();
  while (millis() - startTime < 6000) { // 运行6秒
    static int angle2 = 90;
    static int angle3 = 45;
    static bool increasing2 = true;
    static bool increasing3 = false;

    // 控制第二和第三个舵机 (同时动)
    if (increasing2) {
      angle2++;
      if (angle2 >= 140) {
        increasing2 = false;
      }
    } else {
      angle2--;
      if (angle2 <= 95) {
        increasing2 = true;
      }
    }
    servos[1].write(angle2);

    if (increasing3) {
      angle3++;
      if (angle3 >= 45) {
        increasing3 = false;
      }
    } else {
      angle3--;
      if (angle3 <= 0) {
        increasing3 = true;
      }
    }
    servos[2].write(angle3);

    delay(20);
  }
}

void moveServosBarking() {
  unsigned long startTime = millis();
  while (millis() - startTime < 6000) { // 运行6秒
    static int angle1 = 60;
    static int angle2 = 95;
    static int angle3 = 45;
    static bool increasing1 = true;

    // 控制第一个舵机 (一直动)
    if (increasing1) {
      angle1++;
      if (angle1 >= 180) {
        increasing1 = false;
      }
    } else {
      angle1--;
      if (angle1 <= 60) {
        increasing1 = true;
      }
    }
    servos[0].write(angle1);
    delay(15);
  }
}

void handleCount(String count) {
  count.trim(); // 去除首尾空白字符
  int countValue = count.toInt(); // 将字符串转换为整数

  // 检查count值是否变化大于5
  if (previousCount != -1 && abs(countValue - previousCount) > 5) {
    previousCount = countValue; // 更新previousCount值
    controlServos("barking"); // 进入第三个stage
  } else {
    previousCount = countValue; // 更新previousCount值
  }

  // 根据count值进行处理，例如输出到串口
  Serial.print("Processed count value: ");
  Serial.println(countValue);
}
