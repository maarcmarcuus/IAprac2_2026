package cat.tecnocampus.apps_p1_LiraQuezadaCesar;

public class Trip {
    private final String destination;
    private final String country;
    private final int days;
    private final String email;
    private final double budget;
    private final boolean favorite;

    public Trip(String destination, String country, int days, String email, double budget, boolean favorite) {
        this.destination = destination;
        this.country = country;
        this.days = days;
        this.email = email;
        this.budget = budget;
        this.favorite = favorite;
    }

    public String getDestination() { return destination; }
    public String getCountry() { return country; }
    public int getDays() { return days; }
    public String getEmail() { return email; }
    public double getBudget() { return budget; }
    public boolean isFavorite() { return favorite; }
}
