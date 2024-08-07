package daq.pubber;

import static com.google.udmi.util.GeneralUtils.deepCopy;
import static com.google.udmi.util.GeneralUtils.friendlyStackTrace;
import static java.lang.String.format;

import java.util.concurrent.atomic.AtomicBoolean;
import udmi.schema.Config;
import udmi.schema.Metadata;
import udmi.schema.PubberConfiguration;

/**
 * Wrapper for a complete device construct.
 */
public class ProxyDevice extends ManagerBase implements ManagerHost {

  final DeviceManager deviceManager;
  final Pubber pubberHost;
  private final AtomicBoolean active = new AtomicBoolean();

  /**
   * New instance.
   */
  public ProxyDevice(ManagerHost host, String id, PubberConfiguration config) {
    super(host, makeProxyConfiguration(id, config));
    // Simple shortcut to get access to some foundational mechanisms inside of Pubber.
    pubberHost = (Pubber) host;
    deviceManager = new DeviceManager(this, makeProxyConfiguration(id, config));
  }

  private static PubberConfiguration makeProxyConfiguration(String id, PubberConfiguration config) {
    PubberConfiguration proxyConfiguration = deepCopy(config);
    proxyConfiguration.deviceId = id;
    return proxyConfiguration;
  }

  protected void activate() {
    try {
      active.set(false);
      MqttDevice mqttDevice = pubberHost.getMqttDevice(deviceId);
      mqttDevice.registerHandler(MqttDevice.CONFIG_TOPIC, this::configHandler, Config.class);
      mqttDevice.connect(deviceId);
      deviceManager.activate();
      active.set(true);
      info("Activated proxy device " + deviceId);
    } catch (Exception e) {
      error(format("Could not connect proxy device %s: %s", deviceId, friendlyStackTrace(e)));
    }
  }

  void configHandler(Config config) {
    pubberHost.configPreprocess(deviceId, config);
    deviceManager.updateConfig(config);
    pubberHost.publisherConfigLog("apply", null, deviceId);
  }

  @Override
  protected void shutdown() {
    deviceManager.shutdown();
  }

  @Override
  protected void stop() {
    deviceManager.stop();
  }

  @Override
  public void publish(Object message) {
    if (active.get()) {
      pubberHost.publish(deviceId, message);
    }
  }

  @Override
  public void update(Object update) {
    String simpleName = update.getClass().getSimpleName();
    warn(format("Ignoring proxy device %s update for %s", deviceId, simpleName));
  }

  @Override
  public FamilyProvider getLocalnetProvider(String family) {
    return host.getLocalnetProvider(family);
  }

  public void setMetadata(Metadata metadata) {
    deviceManager.setMetadata(metadata);
  }
}
