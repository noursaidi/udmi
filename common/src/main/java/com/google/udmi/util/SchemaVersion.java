package com.google.udmi.util;

import static com.google.common.base.Preconditions.checkState;

import java.util.AbstractMap.SimpleEntry;
import java.util.HashMap;
import java.util.Map;

/**
 * Formalized enums of the UDMI schema version.
 */
public enum SchemaVersion {
  VERSION_1_5_2("1.5.2", 15020),
  VERSION_1_5_1("1.5.1", 15010),
  VERSION_1_5_0("1.5.0", 15000),
  VERSION_1_4_2("1.4.2", 14020),
  VERSION_1_4_1("1.4.1", 14010),
  VERSION_1_4_0("1.4.0", 14000),
  VERSION_1_3_14("1.3.14", 13014),
  VERSION_1_3_13("1.3.13", 13013),
  VERSION_1("1", 10000);

  public static final SchemaVersion CURRENT;

  public static final Integer LEGACY_REPLACEMENT = 1;

  private static final Map<String, SchemaVersion> CONSTANTS = new HashMap<>();

  static {
    SimpleEntry<SchemaVersion, Integer> max = new SimpleEntry<>(null, 0);
    for (SchemaVersion c : values()) {
      CONSTANTS.put(c.key, c);
      if (c.value > max.getValue()) {
        max = new SimpleEntry<>(c, c.value);
      }
    }
    CURRENT = max.getKey();
  }

  private final String key;
  private final int value;

  SchemaVersion(String key, int value) {
    this.key = key;
    this.value = value;
  }

  public static SchemaVersion fromKey(String key) {
    checkState(CONSTANTS.containsKey(key), "unrecognized schema version " + key);
    return CONSTANTS.get(key);
  }

  public String key() {
    return key;
  }

  public int value() {
    return value;
  }

}
