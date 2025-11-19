// package tech.wenisch.ipfix.generator.config;

// public class IpfixConfig {
//     private String srcIpRange;
//     private String dstIpRange;
//     private String srcPortRange;
//     private String dstPortRange;

//     // Getters and Setters
//     public String getSrcIpRange() {
//         return srcIpRange;
//     }

//     public void setSrcIpRange(String srcIpRange) {
//         this.srcIpRange = srcIpRange;
//     }

//     public String getDstIpRange() {
//         return dstIpRange;
//     }

//     public void setDstIpRange(String dstIpRange) {
//         this.dstIpRange = dstIpRange;
//     }

//     public String getSrcPortRange() {
//         return srcPortRange;
//     }

//     public void setSrcPortRange(String srcPortRange) {
//         this.srcPortRange = srcPortRange;
//     }

//     public String getDstPortRange() {
//         return dstPortRange;
//     }

//     public void setDstPortRange(String dstPortRange) {
//         this.dstPortRange = dstPortRange;
//     }

//     @Override
// public String toString() {
//     return "srcIpRange=" + srcIpRange + ", dstIpRange=" + dstIpRange +
//            ", srcPortRange=" + srcPortRange + ", dstPortRange=" + dstPortRange;
// }
// }
package tech.wenisch.ipfix.generator.config;

import java.util.List;

public class IpfixConfig {
    private List<String> srcIpRange;
    private String dstIpRange;
    private String srcPortRange;
    private String dstPortRange;

    // Getters and Setters
    public List<String> getSrcIpRange() {
        return srcIpRange;
    }

    public void setSrcIpRange(List<String> srcIpRange) {
        this.srcIpRange = srcIpRange;
    }

    public String getDstIpRange() {
        return dstIpRange;
    }

    public void setDstIpRange(String dstIpRange) {
        this.dstIpRange = dstIpRange;
    }

    public String getSrcPortRange() {
        return srcPortRange;
    }

    public void setSrcPortRange(String srcPortRange) {
        this.srcPortRange = srcPortRange;
    }

    public String getDstPortRange() {
        return dstPortRange;
    }

    public void setDstPortRange(String dstPortRange) {
        this.dstPortRange = dstPortRange;
    }

    @Override
public String toString() {
    return "srcIpRange=" + srcIpRange + ", dstIpRange=" + dstIpRange +
           ", srcPortRange=" + srcPortRange + ", dstPortRange=" + dstPortRange;
}
}