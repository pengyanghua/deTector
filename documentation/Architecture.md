## Architecture

deTector includes four loosely coupled components: a controller, a diagnoser, pingers and responders.

![Alt text](https://github.com/yhpeng-git/deTector/blob/master/documentation/System_Architecture.png?raw=true "deTector Architecture")


### Controller

The logical controller periodically constructs the probe matrix indicating the paths for sending probes. We mainly focus on failure localization on links inter-connecting switches, as the fault on a link connecting a server with a ToR switch can be easily identified as discussed in the next paragraph. The probe matrix indicates paths between ToRs. Since we do not rely on ToRs with pinging capability, probes are sent by 2-4 selected servers (pingers) under each ToR.


### Pinger

Each pinger receives the pinglist from the controller, which contains server targets, probe format and ping configuration. The probe paths from a ToR switch to different destinations are distributed among the pinglists of pingers under the ToR switch. The number of probe paths for each pinger is no more than a hundred even for a large DCN. The probe packets are sent over UDP for simplicity. Though TCP is used to carry most traffic in a DCN, the DCN does not differentiate TCP and UDP traffic (e.g., the forwarding behavior) in the vast majority of cases, and hence UDP probes can also manifest network performance. When a pinger detects a probe loss, it confirms the loss pattern by sending two probe packets of the same content additionally.

### Responder

The responder is a lightweight module running on all servers. Upon receiving a probe packet, the responder echoes it back. A responder does not retain any states and all probing results are logged by pingers.


### Diagnoser

Each pinger records packet loss information, and sends it to the diagnoser for loss localization. These logs are saved into a database for real-time analysis and later queries. The diagnoser runs the PLL algorithm to pinpoint packet losses and estimates the loss rates of suspected links.
