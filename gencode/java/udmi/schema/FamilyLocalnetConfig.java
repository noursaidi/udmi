
package udmi.schema;

import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * Family Localnet Config
 * <p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "addr"
})
@Generated("jsonschema2pojo")
public class FamilyLocalnetConfig {

    @JsonProperty("addr")
    public String addr;

    @Override
    public int hashCode() {
        int result = 1;
        result = ((result* 31)+((this.addr == null)? 0 :this.addr.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof FamilyLocalnetConfig) == false) {
            return false;
        }
        FamilyLocalnetConfig rhs = ((FamilyLocalnetConfig) other);
        return ((this.addr == rhs.addr)||((this.addr!= null)&&this.addr.equals(rhs.addr)));
    }

}
