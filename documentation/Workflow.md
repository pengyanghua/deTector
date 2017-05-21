## Workflow Overview

deTector works in three steps in cycles: path computation, network probing and loss localization.

### Path computation

At the beginning of each cycle, the controller reads the data center topology and server health from data center management service, and selects the minimal number of probe paths. The controller then selects pingers in each ToR, constructs and dispatches the pinglists to them.

### Network probing

Next, probe packets are sent along the specified paths across the DCN. Since data center usually adopts ECMP for load balancing, we have to use source routing to control the path traveled by each probe packet, which can be implemented using various methods. A general and feasible solution is to employ packet encapsulation and decapsulation to create end-to-end tunnels.

### Loss localization 
The probe loss measurements are aggregated and analyzed by our loss localization algorithm on the diagnoser. We pinpoint the faulty links, estimate the loss rates, and send alerts to the network operator for further action. The operator can take the faulty links down or repair the links, by identifying the root causes of the failures possibly with the help of other data (e.g., hardware details).
