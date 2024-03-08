const AWSIoTData = require("aws-iot-device-sdk");

// Configure AWS IoT
const endpoint = EXAMPLEDOMAIN;
const certPath = EXAMPLECERT;
const keyPath = EXAMPLEKEY;
const rootCAPath = EXAMPLEPEM;

// Configure MQTT client
const clientId = "SignalDisplayDevice";
const topic = "data/mqtt/signals";

// Create and configure the MQTT client
const mqttClient = AWSIoTData.device({
  keyPath: keyPath,
  certPath: certPath,
  caPath: rootCAPath,
  clientId: clientId,
  host: endpoint,
});

// Connect to AWS IoT
mqttClient.on("connect", function () {
  console.log("Connected to AWS IoT");
  mqttClient.subscribe(topic);
});

// Function to handle incoming messages
mqttClient.on("message", function (topic, payload) {
  const payloadString = payload.toString("utf-8");
  const jsonData = JSON.parse(payloadString);

  console.log("Received message:", jsonData);
});

// Handle errors
mqttClient.on("error", function (error) {
  console.error("AWS IoT Error:", error);
});

// Keep the script running
setInterval(function () {}, 1000);
