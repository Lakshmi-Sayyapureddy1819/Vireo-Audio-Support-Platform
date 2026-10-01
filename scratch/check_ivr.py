import pandas as pd

tickets = pd.read_csv("data/tickets.csv")

def check_failed_ivr(msg):
    if not isinstance(msg, str):
        return True
    m = msg.lower()
    if "[ivr transcript]" in m:
        rem = m.replace("[ivr transcript]", "").strip()
        if len(rem) < 15 or any(w in rem for w in ["unintelligible", "garbled", "silence", "cut off", "no audio", "failed", "incomprehensible"]):
            return True
    return False

failed = tickets[tickets["customer_message"].apply(check_failed_ivr)]
print("Total failed IVR transcripts detected:", len(failed))
print("\nSample failed IVR tickets:")
for idx, row in failed.head(10).iterrows():
    print(f"{row['ticket_id']}: {row['customer_message']}")
