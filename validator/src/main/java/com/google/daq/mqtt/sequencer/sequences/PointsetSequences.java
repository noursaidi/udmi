package com.google.daq.mqtt.sequencer.sequences;

import static com.google.daq.mqtt.util.TimePeriodConstants.THREE_MINUTES_MS;
import static com.google.daq.mqtt.util.TimePeriodConstants.TWO_MINUTES_MS;
import static com.google.udmi.util.GeneralUtils.catchToElse;
import static com.google.udmi.util.GeneralUtils.ifNotNullGet;
import static com.google.udmi.util.GeneralUtils.ifTrueThen;
import static com.google.udmi.util.GeneralUtils.prefixedDifference;
import static com.google.udmi.util.JsonUtil.isoConvert;
import static java.lang.String.format;
import static java.util.Objects.requireNonNull;
import static java.util.Optional.ofNullable;
import static udmi.schema.Bucket.POINTSET;
import static udmi.schema.Category.POINTSET_POINT_INVALID;
import static udmi.schema.Category.POINTSET_POINT_INVALID_VALUE;
import static udmi.schema.FeatureDiscovery.FeatureStage.STABLE;

import com.google.common.collect.ImmutableSet;
import com.google.daq.mqtt.sequencer.Feature;
import com.google.daq.mqtt.sequencer.PointsetBase;
import com.google.daq.mqtt.sequencer.Summary;
import com.google.daq.mqtt.sequencer.ValidateSchema;
import com.google.daq.mqtt.util.SamplingRange;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;
import org.junit.Before;
import org.junit.Test;
import udmi.schema.Envelope.SubFolder;
import udmi.schema.Level;
import udmi.schema.PointPointsetConfig;
import udmi.schema.PointPointsetState;
import udmi.schema.PointsetEvents;

/**
 * Validate pointset related functionality.
 */
public class PointsetSequences extends PointsetBase {

  private static final Duration EVENT_WAIT_DURATION = Duration.ofMinutes(1);
  private static final String EXTRANEOUS_POINT = "extraneous_point";
  private static final String POINTS_MAP_PATH = "pointset.points";
  private static final int DEFAULT_SAMPLE_RATE_SEC = 10;

  @Before
  public void setupExpectedParameters() {
    allowDeviceStateChange("pointset.");
  }

  private boolean isErrorState(PointPointsetState pointState) {
    return ofNullable(catchToNull(() -> pointState.status.level)).orElse(Level.INFO.value())
        >= Level.ERROR.value();
  }

  private void untilPointsetSanity() {
    Set<String> metadataPoints = catchToElse(() ->
        deviceMetadata.pointset.points.keySet(), ImmutableSet.of());
    Set<String> configPoints = catchToElse(() ->
        deviceConfig.pointset.points.keySet(), ImmutableSet.of());
    Set<String> expectedPoints = new HashSet<>(metadataPoints);
    expectedPoints.retainAll(configPoints);
    untilPointsetSanity(expectedPoints);
  }

  private void untilPointsetSanity(Set<String> expectedEventPoints) {
    whileDoing("checking pointset sanity", () -> {

      waitUntil("pointset state matches config", EVENT_WAIT_DURATION, () -> {
        Set<String> configPoints = catchToElse(() -> deviceConfig.pointset.points.keySet(),
            ImmutableSet.of());
        Set<String> statePoints = catchToElse(() -> deviceState.pointset.points.keySet(),
            ImmutableSet.of());
        String prefix = format("config %s state %s differences: ",
            isoConvert(deviceConfig.timestamp), isoConvert(deviceState.timestamp));
        return prefixedDifference(prefix, configPoints, statePoints);
      });

      final AtomicReference<String> message = new AtomicReference<>("no pointset events received");
      waitUntil("pointset event contains correct points", EVENT_WAIT_DURATION, () -> {
        List<PointsetEvents> events = popReceivedEvents(PointsetEvents.class);
        for (PointsetEvents event : events) {
          Set<String> eventPoints = catchToElse(() -> event.points.keySet(),
              ImmutableSet.of());
          String prefix = format("expected %s event %s differences: ",
              isoConvert(deviceConfig.timestamp), isoConvert(event.timestamp));
          String diff = prefixedDifference(prefix, expectedEventPoints, eventPoints);
          message.set(diff);
          if (diff == null) {
            return null;
          }
        }
        return message.get();
      });
    });
  }


  @Test(timeout = TWO_MINUTES_MS)
  @Summary("Check error when pointset configuration contains extraneous point")
  @Feature(stage = STABLE, bucket = POINTSET)
  public void pointset_request_extraneous() {
    deviceConfig.pointset.sample_rate_sec = DEFAULT_SAMPLE_RATE_SEC;

    untilPointsetSanity();

    mapSemanticKey(POINTS_MAP_PATH, EXTRANEOUS_POINT, "extraneous_point", "point configuration");

    deviceConfig.pointset.points.put(EXTRANEOUS_POINT, new PointPointsetConfig());

    try {
      untilTrue("pointset state contains extraneous point error",
          () -> ifNotNullGet(deviceState.pointset.points.get(EXTRANEOUS_POINT),
              state -> state.status.category.equals(POINTSET_POINT_INVALID)
                  && state.status.level.equals(POINTSET_POINT_INVALID_VALUE)));
      // When requesting an extraneous point, the device should still only report metadata points.
      untilPointsetSanity();
    } finally {
      deviceConfig.pointset.points.remove(EXTRANEOUS_POINT);
    }

    untilTrue("pointset state removes extraneous point error",
        () -> !deviceState.pointset.points.containsKey(EXTRANEOUS_POINT));

    untilPointsetSanity();
  }

  @Test(timeout = THREE_MINUTES_MS)
  @Summary("Check that pointset state does not report an unconfigured point")
  @Feature(stage = STABLE, bucket = POINTSET)
  public void pointset_remove_point() {
    deviceConfig.pointset.sample_rate_sec = 10;
    untilPointsetSanity();

    List<String> candidatePoints = new ArrayList<>(deviceConfig.pointset.points.keySet());
    ifTrueThen(candidatePoints.isEmpty(), () -> skipTest("No points to remove"));
    String name = candidatePoints.get((int) Math.floor(Math.random() * candidatePoints.size()));

    debug("Removing randomly selected test point " + name);
    mapSemanticKey(POINTS_MAP_PATH, name, "random_point", "point configuration");
    PointPointsetConfig removed = requireNonNull(deviceConfig.pointset.points.remove(name));

    try {
      untilFalse("pointset state does not contain removed point",
          () -> deviceState.pointset.points.containsKey(name));
      // After removing the point from config, the device should stop reporting it in telemetry.
      untilPointsetSanity();
    } finally {
      deviceConfig.pointset.points.put(name, removed);
    }

    untilTrue("pointset state contains restored point",
        () -> deviceState.pointset.points.containsKey(name));

    untilPointsetSanity();
  }

  /**
   * Simple check that device publishes pointset events.
   */
  @Test(timeout = TWO_MINUTES_MS)
  @Summary("Check that a device publishes pointset events")
  @Feature(stage = STABLE, bucket = POINTSET, nostate = true)
  @ValidateSchema(SubFolder.POINTSET)
  public void pointset_publish() {
    ifNullSkipTest(deviceConfig.pointset, "no pointset found in config");
    deviceConfig.pointset.sample_rate_sec = DEFAULT_SAMPLE_RATE_SEC;
    popReceivedEvents(PointsetEvents.class);
    untilPointsetSanity();
  }

  /**
   * Generates message for checking the time periods are within the sampling range.
   */
  private String samplingMessagesCheckMessage(SamplingRange samplingRange) {
    return format("time period between successive pointset events is %s",
        samplingRange);
  }

  /**
   * Tests both sample_rate_sec and sample_limit_sec by defining two non-intersecting narrow ranges
   * of both parameters, and ensuring telemetry is within this range.
   */
  @Test(timeout = THREE_MINUTES_MS)
  @Summary("Check handling of sample_rate_sec and sample_limit_sec")
  @Feature(stage = STABLE, bucket = POINTSET, nostate = true)
  @ValidateSchema(SubFolder.POINTSET)
  public void pointset_publish_interval() {
    ifNullSkipTest(deviceConfig.pointset, "no pointset found in config");

    // Test two narrow non-intersecting windows
    SamplingRange firstRange = new SamplingRange(5, 8, 1.5);
    testPointsetWithSamplingRange(firstRange, 4, 1);

    SamplingRange secondRange = new SamplingRange(15, 18, 1.5);
    testPointsetWithSamplingRange(secondRange, 4, 1);
  }

  /**
   * Given a list of events, sorts these in timestamp order and returns a list of the the intervals
   * between each pair of successive messages based on the in-payload timestamp.
   */
  private List<Long> intervalFromEvents(List<PointsetEvents> receivedEvents) {
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
   * Updating the sample_limit_sec and sample_rate_sec according to provided SamplingRange and
   * checks if the interval between subsequent pointset events are within this range.
   */
  private void testPointsetWithSamplingRange(SamplingRange sampleRange, Integer messagesToSample,
      Integer intervalsToIgnore) {
    if (messagesToSample < 2) {
      throw new RuntimeException("cannot test with less than two messages");
    } else if (intervalsToIgnore > messagesToSample - 1) {
      throw new RuntimeException("cannot ignore more intervals than intervals measured");
    }

    deviceConfig.pointset.sample_limit_sec = sampleRange.sampleLimit;
    deviceConfig.pointset.sample_rate_sec = sampleRange.sampleRate;

    popReceivedEvents(PointsetEvents.class);
    untilTrue(format("receive at least %d pointset events", messagesToSample),
        () -> (countReceivedEvents(PointsetEvents.class) > messagesToSample)
    );

    List<PointsetEvents> receivedEvents = popReceivedEvents(PointsetEvents.class);
    List<Long> intervals = intervalFromEvents(receivedEvents);

    if (intervalsToIgnore > 0) {
      intervals.subList(0, intervalsToIgnore).clear();
    }

    checkThat(samplingMessagesCheckMessage(sampleRange),
        () -> sampleRange.doesIntersect(intervals)
    );

  }

}


