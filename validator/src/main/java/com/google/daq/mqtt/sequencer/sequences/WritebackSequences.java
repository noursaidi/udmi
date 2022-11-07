package com.google.daq.mqtt.sequencer.sequences;
import com.google.daq.mqtt.sequencer.PointSequencer;
import com.google.udmi.util.JsonUtil;
import java.util.Map;
import java.util.Objects;
import org.junit.Test;
import java.util.List;
import udmi.schema.DiscoveryEvent;
import udmi.schema.Envelope.SubFolder;
import udmi.schema.PointPointsetState.Value_state;
import udmi.schema.TargetTestingModel;
import udmi.schema.PointsetEvent;
import udmi.schema.PointPointsetEvent;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 * Validate UDMI writeback capabilities.
 */
public class WritebackSequences extends PointSequencer {

  public static final String INVALID_STATE = "invalid";
  public static final String FAILURE_STATE = "failure";
  public static final String APPLIED_STATE = "applied";
  public static final String DEFAULT_STATE = null;

  private boolean valueStateIs(String pointName, String expected) {
    if (deviceState.pointset == null || !deviceState.pointset.points.containsKey(pointName)) {
      return false;
    }
    Value_state rawState = deviceState.pointset.points.get(pointName).value_state;
    String valueState = rawState == null ? null : rawState.value();
    boolean equals = Objects.equals(expected, valueState);
    debug(String.format("%s Value state %s equals %s = %s%n",
        JsonUtil.getTimestamp(), expected, valueState, equals));
    return equals;
  }

  private String expectedValueState(String pointName, String expectedValue) {
    String targetState = expectedValue == null ? "default (null)" : expectedValue;
    return String.format("point %s to have value_state %s", pointName, targetState);
  }

  private String expectedPresentValue(String pointName, Object expectedValue) {
    return String.format("point `%s` to have present_value `%s`", pointName, expectedValue);
  }

  private PointsetEvent nextPointsetEvent() {
    List<PointsetEvent> messages = getReceivedEvents(PointsetEvent.class);
    return JsonUtil.convertTo(PointsetEvent.class, messages.get(0));
  }


  private boolean presentValueIs(String pointName, Object desiredValue) {
    info("received events: " + Integer.toString(countReceivedEvents(PointsetEvent.class)));
    List<PointsetEvent> messages = getReceivedEvents(PointsetEvent.class);
    for (PointsetEvent message : messages) {
      PointsetEvent pointsetEvent = JsonUtil.convertTo(PointsetEvent.class, message);
      if (pointsetEvent.points.get(pointName) == null) {
        return false;
      }
      info("Value " + pointsetEvent.points.get(pointName).present_value);
      info("desired value is " + desiredValue);
      info((desiredValue == pointsetEvent.points.get(pointName).present_value) ? "yes" : "no");
      if (pointsetEvent.points.get(pointName).present_value == desiredValue) {
        return true;
      }
    }
    return false;
  }


  @Test
  public void writeback_success_apply() {
    TargetTestingModel appliedTarget = getTarget(APPLIED_STATE);
    String appliedPoint = appliedTarget.target_point;
    Object appliedValue = appliedTarget.target_value;

    deviceConfig.pointset.points.get(appliedPoint).set_value = appliedValue;
    updateConfig();
    info("received events: " + Integer.toString(countReceivedEvents(PointsetEvent.class)));
    getReceivedEvents(PointsetEvent.class);
    info("received events: " + Integer.toString(countReceivedEvents(PointsetEvent.class)));
    untilTrue("receive one pointset event",
        () -> (countReceivedEvents(PointsetEvent.class) > 0)
    );

    PointsetEvent nextPointsetEvent = nextPointsetEvent();
    assertTrue((nextPointsetEvent.points.get(appliedPoint) != null));
    assertEquals(appliedValue, nextPointsetEvent.points.get(appliedPoint).present_value);
  }

  @Test
  public void writeback_success_state() {
    TargetTestingModel appliedTarget = getTarget(APPLIED_STATE);
    String appliedPoint = appliedTarget.target_point;
    Object appliedValue = appliedTarget.target_value;

    deviceConfig.pointset.points.get(appliedPoint).set_value = appliedValue;
    updateConfig();

    untilTrue(expectedValueState(appliedPoint, APPLIED_STATE),
        () -> valueStateIs(appliedPoint, APPLIED_STATE)
    );

    //Info("received events: " + Integer.toString(countReceivedEvents(PointsetEvent.class)));
    //getReceivedEvents(PointsetEvent.class);
    info("received events: " + Integer.toString(countReceivedEvents(PointsetEvent.class)));
    info("cleared");
    getReceivedEvents(PointsetEvent.class);
    untilTrue(expectedPresentValue(appliedPoint, appliedValue),
      () -> presentValueIs(appliedPoint, appliedValue)
    );

    /* 
    info("now > 0");
    info("received events: " + Integer.toString(countReceivedEvents(PointsetEvent.class)));
  
    PointsetEvent nextPointsetEvent = nextPointsetEvent();
    info(JsonUtil.getTimestamp(nextPointsetEvent.timestamp));
    assertTrue((nextPointsetEvent.points.get(appliedPoint) != null));
    assertEquals(appliedValue, nextPointsetEvent.points.get(appliedPoint).present_value);
    */
  }

}
