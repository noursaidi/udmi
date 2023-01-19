
package udmi.schema;

import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * Site Metadata Location
 * <p>
 * Location of the site or building
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "address",
    "lat",
    "long"
})
@Generated("jsonschema2pojo")
public class SiteMetadataLocation {

    /**
     * Postal address of the site
     * 
     */
    @JsonProperty("address")
    @JsonPropertyDescription("Postal address of the site")
    public String address;
    /**
     * Latitude of the site in WGS84 coordinates, as indicated by a map marker 
     * 
     */
    @JsonProperty("lat")
    @JsonPropertyDescription("Latitude of the site in WGS84 coordinates, as indicated by a map marker ")
    public Double lat;
    /**
     * Longitude of the site in WGS84 coordinates, as indicated by a map marker
     * 
     */
    @JsonProperty("long")
    @JsonPropertyDescription("Longitude of the site in WGS84 coordinates, as indicated by a map marker")
    public Double _long;

    @Override
    public int hashCode() {
        int result = 1;
        result = ((result* 31)+((this.address == null)? 0 :this.address.hashCode()));
        result = ((result* 31)+((this.lat == null)? 0 :this.lat.hashCode()));
        result = ((result* 31)+((this._long == null)? 0 :this._long.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof SiteMetadataLocation) == false) {
            return false;
        }
        SiteMetadataLocation rhs = ((SiteMetadataLocation) other);
        return ((((this.address == rhs.address)||((this.address!= null)&&this.address.equals(rhs.address)))&&((this.lat == rhs.lat)||((this.lat!= null)&&this.lat.equals(rhs.lat))))&&((this._long == rhs._long)||((this._long!= null)&&this._long.equals(rhs._long))));
    }

}