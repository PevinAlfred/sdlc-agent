# This code acts as a simple incident manager that can be used to log incidents.
# It can be extended to include more complex logic such as notifying teams, integrating with monitoring systems, etc.

def raise_incident(details: str):
    print(f"[INCIDENT] Created: {details}")

if __name__ == "__main__":
    raise_incident("Example service down")
