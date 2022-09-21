package com.google.daq.mqtt.sequencer.sequences;

import com.google.daq.mqtt.sequencer.PointSequencer;
import com.google.daq.mqtt.util.JsonUtil;
import java.util.Objects;
import org.junit.Test;
import java.util.List;
import udmi.schema.PointPointsetState.Value_state;
import udmi.schema.TargetTestingModel;
import udmi.schema.PointsetEvent;
import udmi.schema.PointPointsetEvent;

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
    Value_state rawState = deviceState.pointset. .get(pointName).value_state;
    String valueState = rawState == null ? null : rawState.value();
    boolean equals = Objects.equals(expected, valueState);
    System.err.printf("%s Value state %s equals %s = %s%n",
        JsonUtil.getTimestamp(), expected, valueState, equals);
    return equals;
  }

  private String expectedValueState(String pointName, String expectedValue) {
    String targetState = expectedValue == null ? "default (null)" : expectedValue;
    return String.format("point %s to have value_state %s", pointName, targetState);
  }

  @Test
  public void writeback_success() {

    TargetTestingModel appliedTarget = getTarget(APPLIED_STATE);


    String appliedPoint = appliedTarget.target_point;
    deviceConfig.pointset.points.get(appliedPoint).set_value = appliedTarget.target_value;
    pointValueNow(appliedPoint, appliedTarget.target_value);




  }
}
