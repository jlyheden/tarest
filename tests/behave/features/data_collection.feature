Feature: Data collection

  Scenario: Scraping and storing data from Yahoo Finance
    Given the ticker ^OMX
    When I ask Yahoo Finance for historical data between 2015-01-01 and 2015-02-01
    And I store the historical data in the database
    Then I can query the stored data
    And I get 20 records back

  Scenario: Scraping and storing data from Yahoo Finance with overlapping data
    Given the ticker ^OMX
    When I ask Yahoo Finance for historical data between 2015-01-01 and 2015-02-01
    And I store the historical data in the database
    And I ask Yahoo Finance for historical data between 2015-01-15 and 2015-02-02
    And I store the historical data in the database
    Then I can query the stored data
    And I get 21 records back