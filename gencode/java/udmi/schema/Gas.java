
package udmi.schema;

import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "carbon_factor",
    "unit_cost"
})
@Generated("jsonschema2pojo")
public class Gas {

    @JsonProperty("carbon_factor")
    public Carbon_factor carbon_factor;
    @JsonProperty("unit_cost")
    public Unit_cost unit_cost;

    @Override
    public int hashCode() {
        int result = 1;
        result = ((result* 31)+((this.carbon_factor == null)? 0 :this.carbon_factor.hashCode()));
        result = ((result* 31)+((this.unit_cost == null)? 0 :this.unit_cost.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof Gas) == false) {
            return false;
        }
        Gas rhs = ((Gas) other);
        return (((this.carbon_factor == rhs.carbon_factor)||((this.carbon_factor!= null)&&this.carbon_factor.equals(rhs.carbon_factor)))&&((this.unit_cost == rhs.unit_cost)||((this.unit_cost!= null)&&this.unit_cost.equals(rhs.unit_cost))));
    }

}
