package com.google.daq.mqtt.sequencer.sequences;

import static com.google.daq.mqtt.util.TimePeriodConstants.FOUR_MINUTES_MS;
import static com.google.daq.mqtt.util.TimePeriodConstants.THREE_MINUTES_MS;
import static com.google.daq.mqtt.util.TimePeriodConstants.TWO_MINUTES_MS;
import static com.google.udmi.util.CleanDateFormat.dateEquals;
import static com.google.udmi.util.JsonUtil.getTimestamp;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static udmi.schema.Category.SYSTEM_CONFIG_APPLY;
import static udmi.schema.Category.SYSTEM_CONFIG_APPLY_LEVEL;
import static udmi.schema.Category.SYSTEM_CONFIG_PARSE;
import static udmi.schema.Category.SYSTEM_CONFIG_PARSE_LEVEL;
import static udmi.schema.Category.SYSTEM_CONFIG_RECEIVE;
import static udmi.schema.Category.SYSTEM_CONFIG_RECEIVE_LEVEL;

import com.google.daq.mqtt.sequencer.SequenceBase;
import com.google.daq.mqtt.sequencer.SkipTest;
import com.google.daq.mqtt.util.SamplingRange;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.Test;
import udmi.schema.Entry;
import udmi.schema.Level;
import udmi.schema.PointsetEvent;

/**
 * Validate basic device configuration handling operation, not specific to any device function.
 */
public class ConfigSequences extends SequenceBase {

  @Test(timeout = TWO_MINUTES_MS)
  @Description("Check that last_update state is correctly set in response to a config update.")
  public void system_last_update() {
    untilTrue("state last_config matches config timestamp", () -> {
      Date expectedConfig = deviceConfig.timestamp;
      Date lastConfig = deviceState.system.last_config;
      return dateEquals(expectedConfig, lastConfig);
    });
  }

  @Test(timeout = TWO_MINUTES_MS)
  @Description("Check that the min log-level config is honored by the device.")
  public void system_min_loglevel() {
    clearLogs();
    Integer savedLevel = deviceConfig.system.min_loglevel;
    deviceConfig.system.min_loglevel = Level.WARNING.value();
    hasNotLogged(SYSTEM_CONFIG_APPLY, SYSTEM_CONFIG_APPLY_LEVEL);
    deviceConfig.system.min_loglevel = savedLevel;
    hasLogged(SYSTEM_CONFIG_APPLY, SYSTEM_CONFIG_APPLY_LEVEL);
  }

  @Test(timeout = TWO_MINUTES_MS)
  @Description("Check that the device MQTT-acknowledges a sent config.")
  public void device_config_acked() {
    untilTrue("config acked", () -> configAcked);
  }

  @Test(timeout = TWO_MINUTES_MS)
  @Description("Check that the device correctly handles a broken (non-json) config message.")
  public void broken_config() {
    deviceConfig.system.min_loglevel = Level.DEBUG.value();
    untilFalse("no interesting status", this::hasInterestingSystemStatus);
    untilTrue("clean config/state synced", this::configUpdateComplete);
    Date stableConfig = deviceConfig.timestamp;
    info("initial stable_config " + getTimestamp(stableConfig));
    untilTrue("state synchronized", () -> dateEquals(stableConfig, deviceState.system.last_config));
    info("initial last_config " + getTimestamp(deviceState.system.last_config));
    checkThat("initial stable_config matches last_config",
        () -> dateEquals(stableConfig, deviceState.system.last_config));
    clearLogs();
    extraField = "break_json";
    hasLogged(SYSTEM_CONFIG_RECEIVE, SYSTEM_CONFIG_RECEIVE_LEVEL);
    untilTrue("has interesting status", this::hasInterestingSystemStatus);
    Entry stateStatus = deviceState.system.status;
    info("Error message: " + stateStatus.message);
    info("Error detail: " + stateStatus.detail);
    assertEquals(SYSTEM_CONFIG_PARSE, stateStatus.category);
    assertEquals(Level.ERROR.value(), (int) stateStatus.level);
    info("following stable_config " + getTimestamp(stableConfig));
    info("following last_config " + getTimestamp(deviceState.system.last_config));
    assertTrue("following stable_config matches last_config",
        dateEquals(stableConfig, deviceState.system.last_config));
    assertTrue("system operational", deviceState.system.operational);
    hasLogged(SYSTEM_CONFIG_PARSE, Level.ERROR);
    hasNotLogged(SYSTEM_CONFIG_APPLY, SYSTEM_CONFIG_APPLY_LEVEL);
    resetConfig(); // clears extra_field
    hasLogged(SYSTEM_CONFIG_RECEIVE, SYSTEM_CONFIG_RECEIVE_LEVEL);
    untilFalse("no interesting status", this::hasInterestingSystemStatus);
    untilTrue("last_config updated",
        () -> !dateEquals(stableConfig, deviceState.system.last_config)
    );
    assertTrue("system operational", deviceState.system.operational);
    hasLogged(SYSTEM_CONFIG_APPLY, SYSTEM_CONFIG_APPLY_LEVEL);
    hasLogged(SYSTEM_CONFIG_PARSE, SYSTEM_CONFIG_PARSE_LEVEL);
  }

  private boolean hasInterestingSystemStatus() {
    return deviceState.system.status != null
        && deviceState.system.status.level >= Level.WARNING.value();
  }

  private boolean hasInterestingPointsetStatus() {
    return deviceState.pointset.status != null
        && deviceState.pointset.status.level >= Level.WARNING.value();
  }

  @Test(timeout = TWO_MINUTES_MS)
  @Description("Check that the device correctly handles an extra out-of-schema field")
  public void extra_config() {
    deviceConfig.system.min_loglevel = Level.DEBUG.value();
    untilTrue("last_config not null", () -> deviceState.system.last_config != null);
    untilTrue("system operational", () -> deviceState.system.operational);
    untilFalse("no interesting status", this::hasInterestingSystemStatus);
    clearLogs();
    final Date prevConfig = deviceState.system.last_config;
    extraField = "Flabberguilstadt";
    hasLogged(SYSTEM_CONFIG_RECEIVE, SYSTEM_CONFIG_RECEIVE_LEVEL);
    untilTrue("last_config updated", () -> !deviceState.system.last_config.equals(prevConfig));
    untilTrue("system operational", () -> deviceState.system.operational);
    untilFalse("no interesting status", this::hasInterestingSystemStatus);
    hasLogged(SYSTEM_CONFIG_PARSE, SYSTEM_CONFIG_PARSE_LEVEL);
    hasLogged(SYSTEM_CONFIG_APPLY, SYSTEM_CONFIG_APPLY_LEVEL);
    final Date updatedConfig = deviceState.system.last_config;
    extraField = null;
    hasLogged(SYSTEM_CONFIG_RECEIVE, SYSTEM_CONFIG_RECEIVE_LEVEL);
    untilTrue("last_config updated again",
        () -> !deviceState.system.last_config.equals(updatedConfig)
    );
    untilTrue("system operational", () -> deviceState.system.operational);
    untilFalse("no interesting status", this::hasInterestingSystemStatus);
    hasLogged(SYSTEM_CONFIG_PARSE, SYSTEM_CONFIG_PARSE_LEVEL);
    hasLogged(SYSTEM_CONFIG_APPLY, SYSTEM_CONFIG_APPLY_LEVEL);
  }

  /**
   * Tests sample_rate_min by measuring the initial interval between the last two messages received,
   * then setting the config.pointset.sample_rate_min to match half the initial interval
   * and measuring the final interval between several messages and ensuring it is less than the new
   * interval (with a tolerance of 1.5s).
   *
   * <p>Pass if: final interval < new sample_rate_min + tolerance
   * Fail if: final interval > new sample_rate_min + tolerance
   * Skip if: initial interval < 5s (too fast for automated test)
   */
  @Test(timeout = THREE_MINUTES_MS)
  @Description("device publishes pointset events at a rate of no more than config sample_rate_sec")
  public void pointset_sample_rate() {
    Integer defaultSampleRate = 10;

    // Clear received events because this could contain messages from a previous sample rate test
    getReceivedEvents(PointsetEvent.class);

    Instant endTime = Instant.now().plusSeconds(defaultSampleRate * 3);
    // To pick the test sample rate, either measure the devices
    // given sampling rate from its last 2 messages and half it or use
    // a value if long
    untilTrue("measure initial sample rate",
        () -> (countReceivedEvents(PointsetEvent.class) > 1
          || Instant.now().isAfter(endTime))
    );

    Integer testSampleRate;
    if (countReceivedEvents(PointsetEvent.class) < 2) {
      // 2 messages not seen, assume interval is longer than wait period, pick a small number
      testSampleRate = defaultSampleRate;
    } else {
      List<PointsetEvent> receivedEvents = getReceivedEvents(PointsetEvent.class);
      List<Long> telemetryDelta = intervalFromEvents(receivedEvents);
      Integer nominalInterval = telemetryDelta.get(0).intValue();
      info(String.format("initial sample rate is %d seconds", nominalInterval));

      if (nominalInterval < 5) {
        throw new SkipTest("measured sample rate is too low for automated test");
      }

      // Use an interval smaller than the devices last interval
      testSampleRate = Math.floorDiv(nominalInterval, 2);
    }

    info(String.format("setting sample rate to %d seconds", testSampleRate));
    SamplingRange testSampleRange = new SamplingRange(1, testSampleRate, 1.5);
    checkThat(samplingMessagesCheckMessage(testSampleRange),
        () -> testPointsetWithSamplingRange(testSampleRange, 5, 2)
    );
  }

  /**
   * Generates message for checking the time periods are within the sampling range.
   *
   * @param samplingRange sampling range to produce message for
   * @return message
   */
  private String samplingMessagesCheckMessage(SamplingRange samplingRange) {
    return String.format("time period between successive pointset events is %s",
        samplingRange);
  }

  /**
   * Tests both sample_rate_sec and sample_limit_sec by defining two non-intersecting narrow
   * ranges of both parameters, and ensuring telemetry is within this range.
   */
  @Test(timeout = 240000)
  @Description("test sample rate and sample limit sec")
  public void pointset_publish_interval() {
    // Test two narrow non-intersecting windows

    SamplingRange firstRange = new SamplingRange(5, 8, 1.5);
    checkThat(samplingMessagesCheckMessage(firstRange),
        () -> testPointsetWithSamplingRange(firstRange, 4, 1)
    );

    SamplingRange secondRange = new SamplingRange(15, 18, 1.5);
    checkThat(samplingMessagesCheckMessage(secondRange),
        () -> testPointsetWithSamplingRange(secondRange, 4, 1)
    );
  }

  /**
   * Given a list of events, sorts these in timestamp order and returns a list of the
   * the intervals between each pair of successive messages based on the in-payload timestamp.
   *
   * @param receivedEvents list of PointsetEvents
   * @return list of the intervals between successive messages
   */
  private List<Long> intervalFromEvents(List<PointsetEvent> receivedEvents) {
    ArrayList<Long> intervals = new ArrayList<>();

    if (receivedEvents.size() < 2) {
      throw new RuntimeException("cannot calculate interval with less than 2 messages");
    }

    List<Date> events = receivedEvents.stream().map(event -> event.timestamp)
        .collect(Collectors.toList());
    Collections.sort(events);
    for (int i = 1; i < events.size(); i++) {
      intervals.add(((events.get(i).getTime() - events.get(i - 1).getTime()) / 1000));
    }
    return intervals;
  }

  /**
   * Updating the sample_limit_sec and sample_rate_sec according to provided SamplingRange
   * and checks if the interval between subsequent pointset events are within this range.
   *
   * @param sampleRange sample range to test with
   * @param messagesToSample number of messages to sample (must be greater than 2)
   * @param intervalsToIgnore number of intervals to ignore at start (to allow system to settle)
   * @return boolean were all messages sampled in the given range
   */
  private boolean testPointsetWithSamplingRange(SamplingRange sampleRange, Integer messagesToSample,
      Integer intervalsToIgnore) {
    if (messagesToSample < 2) {
      throw new RuntimeException("cannot test with less than two messages");
    } else if (intervalsToIgnore > messagesToSample - 1) {
      throw new RuntimeException("cannot ignore more intervals than intervals measured");
    }

    deviceConfig.pointset.sample_limit_sec = sampleRange.sampleLimit;
    deviceConfig.pointset.sample_rate_sec = sampleRange.sampleRate;

    getReceivedEvents(PointsetEvent.class);
    untilTrue(String.format("receive at least %d pointset events", messagesToSample),
        () -> (countReceivedEvents(PointsetEvent.class) > messagesToSample)
    );

    List<PointsetEvent> receivedEvents = getReceivedEvents(PointsetEvent.class);
    List<Long> intervals = intervalFromEvents(receivedEvents);

    if (intervalsToIgnore > 0) {
      intervals.subList(0, intervalsToIgnore).clear();
    }
    return sampleRange.doesIntersect(intervals);
  }

}


