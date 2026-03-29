# Subagent completion hardening (2026)

Why this exists:
- Recent multi-agent SWE work keeps converging on the same failure mode: specialists return incomplete work, and orchestrators accept it too early.
- Recent Claude Code practice also points to the same fix: bounded agents, explicit artifacts, verification, and selective delegation.

Applied protocol in xlfg 2.7.0:
- one atomic task packet in
- one required artifact out
- one honest done check
- foregrounded phase-critical specialists
- same-specialist resume before replacement
- plan-time task splitting when a packet would produce multiple unrelated outputs
