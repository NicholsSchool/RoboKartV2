#include <Arduino.h>
#include <WiFi.h>
#include <zenoh-pico.h>

#define SSID "RoboKart"
#define PASS "Robo1273Wifi"

z_owned_session_t session;
z_owned_publisher_t heartbeatPublisher;

static int idx = 0;

void setup() {

    Serial.begin(9600);
    while (!Serial) {
        delay(1000);
    }

    Serial.println();
    Serial.println("----- ROBOKART KartOS v0.1 -----");
    Serial.println("Serial INIT");

    // WiFi Setup
    Serial.print("Connecting to WiFi.....");
    WiFi.setHostname("RoboKart-DevBoard");
    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);
    WiFi.begin(SSID, PASS);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
    }
    Serial.println("OK");

    //Printing Network Info
    Serial.println("Network Info:");
    Serial.print("| IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("| Subnet Mask: ");
    Serial.println(WiFi.subnetMask());
    Serial.print("| Gateway: ");
    Serial.println(WiFi.gatewayIP());

    delay(2000);

    // Configuration
    z_owned_config_t config;
    z_config_default(&config);
    zp_config_insert(z_config_loan_mut(&config), Z_CONFIG_MODE_KEY, "peer");
    zp_config_insert(z_config_loan_mut(&config), Z_CONFIG_MULTICAST_LOCATOR_KEY, "udp/224.0.0.225:7446");
    zp_config_insert(z_config_loan_mut(&config), Z_CONFIG_LISTEN_KEY, "udp/224.0.0.225:7446#iface=en0");

    delay(500);

    // Session Initialization
    Serial.print("Opening Zenoh Session.....");
    int ret = z_open(&session, z_config_move(&config), NULL);
    if (ret < 0) {
        Serial.println("ERROR " + String(ret));
        ret = z_open(&session, z_config_move(&config), NULL);
        while (1) {
            ;
        }
    }
    Serial.println("OK");

    // Tasks
    if (zp_start_read_task(z_session_loan_mut(&session), NULL) < 0 || zp_start_lease_task(z_session_loan_mut(&session), NULL) < 0) {
        Serial.println("Unable to start read and lease tasks\n");
        z_session_drop(z_session_move(&session));
        while (1) {
            ;
        }
    }

    // Heartbeat Publisher Setup
    Serial.print("Declaring heartbeat publisher.....");
    z_view_keyexpr_t heartbeatKeyExpr;
    z_view_keyexpr_from_str_unchecked(&heartbeatKeyExpr, "Robot/ESPTest/Heartbeat");
    if (z_declare_publisher(z_session_loan(&session), &heartbeatPublisher, z_view_keyexpr_loan(&heartbeatKeyExpr), NULL) < 0) {
        Serial.println("Unable to declare publisher for key expression!");
        while (1) {
            ;
        }
    }
    Serial.println("OK");

    Serial.println("Zenoh setup finished!");

}

void loop() {

  char buf[256];
  sprintf(buf, "[%4d] %s", idx++, "{\"battery\": \"18.00V\"}");

  z_owned_bytes_t payload;
  z_bytes_copy_from_str(&payload, buf);

  if (z_publisher_put(z_publisher_loan(&heartbeatPublisher), z_bytes_move(&payload), NULL) < 0) {
      Serial.println("Error while publishing heartbeat!");
  }

  delay(500);

}