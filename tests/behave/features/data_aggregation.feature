Feature: Data aggregation

  Scenario: Simple Moving Average calculation
    Given some data set
    When I calculate SMA 10 day average on the data set
    Then I get a value of 5.5

  Scenario: RSI14
    Given the ticker ^OMX
    When I ask Yahoo Finance for historical data between 2015-01-01 and 2015-02-01
    And I store the historical data in the database
    And I calculate RSI 14 on the data set
    Then I get a value of 64.2

  Scenario: Simple Moving Average time series
    Given the ticker ^OMX
    When I ask Yahoo Finance for historical data between 2015-01-01 and 2016-01-01
    And I store the historical data in the database
    And I calculate SMA 10 into time series
    Then I get the last value of 1432.8

  Scenario: RSI14 time series
    Given the ticker ^OMX
    When I ask Yahoo Finance for historical data between 2015-01-01 and 2016-01-01
    And I store the historical data in the database
    And I calculate RSI14 into time series
    Then I get the last value of 47.6

  Scenario: EMA 10 time series
    Given the ticker ^OMX
    When I ask Yahoo Finance for historical data between 2015-01-01 and 2016-01-01
    And I store the historical data in the database
    And I calculate EMA10 into time series
    Then I get the last value of 1439.1

  Scenario: MACD time series
    Given the ticker ^OMX
    When I ask Yahoo Finance for historical data between 2015-01-01 and 2016-01-01
    And I store the historical data in the database
    And I calculate MACD with short EMA 12, long EMA 26 and signal EMA 9
    Then I get the last value of 1439.1

  Scenario: Trend calculation
    Given the ticker ^OMX
    When I ask Yahoo Finance for historical data between 2015-01-01 and 2016-01-01
    And I store the historical data in the database
    And I calculate RSI14 into time series
    And I calculate the trend based on 10 days
    Then I get a value of -0.13
