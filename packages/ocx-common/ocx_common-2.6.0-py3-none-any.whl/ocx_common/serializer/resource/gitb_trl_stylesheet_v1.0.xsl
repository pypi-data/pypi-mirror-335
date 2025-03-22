<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tr="http://www.gitb.com/tr/v1/" xmlns:gitb="http://www.gitb.com/core/v1/">

    <xsl:template match="/">
        <xsl:variable name="result" select="//tr:result"/>
        <xsl:variable name="reportItems" select="//tr:reports/*[local-name() = 'error' or local-name() = 'warning' or local-name() = 'info']"/>
        <xsl:variable name="input" select="//tr:context/gitb:item[@name = 'xml' or @name='contentToValidate']/gitb:value"/>
        <html>
            <head><title>Validation report</title></head>
            <body>
                <style>
                    body {
                    font-family: "Open Sans",Arial,sans-serif;
                    font-size: 14px;
                    line-height: 1.4;
                    padding: 0px 10px;
                    }
                    .title {
                    font-size: 30px;
                    margin-top: 20px;
                    margin-bottom: 30px;
                    }
                    .result {
                    font-size: 90%;
                    text-shadow: 1px 1px 0 rgb(90 90 90 / 50%);
                    padding: 0.3em 0.6em 0.3em;
                    font-weight: bold;
                    line-height: 1;
                    color: #fff;
                    text-align: center;
                    white-space: nowrap;
                    vertical-align: baseline;
                    border-radius: 0.25em;
                    }
                    .result.SUCCESS {
                    background-color: #5cb85c;
                    }
                    .result.FAILURE {
                    background-color: #c9302c;
                    }
                    .result.WARNING {
                    background-color: #f0ad4e;
                    }
                    .result.UNDEFINED {
                    background-color: #7c7c7c;
                    }
                    .section {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    margin-bottom: 20px;
                    }
                    .section-title {
                    color: #333;
                    background-color: #f5f5f5;
                    font-size: 18px;
                    padding: 20px 15px;
                    }
                    .section-content {
                    width: 100%;
                    border-top: 1px solid #ddd;
                    }
                    .overview .section-content {
                    display: table;
                    }
                    .overview .section-content {
                    padding: 10px 0px;
                    }
                    .overview .section-content .row {
                    display: table-row;
                    }
                    .label {
                    font-weight: bold;
                    }
                    .overview .section-content .row .label {
                    white-space: nowrap;
                    width: 1%;
                    }
                    .overview .section-content .row .label, .overview .section-content .row .value {
                    display: table-cell;
                    padding: 5px 15px;
                    }
                    .report-item {
                    margin: 10px;
                    border-bottom-right-radius: 20px;
                    border-top-right-radius: 20px;
                    border-bottom-left-radius: 4px;
                    border-top-left-radius: 4px;
                    }
                    .details .metadata .row {
                    display: flex;
                    }
                    .details .metadata .row .label {
                    display: flex;
                    margin-right: 10px;
                    }
                    .report-item.error {
                    background-color: #c9302c;
                    }
                    .report-item.warning {
                    background-color: #f0ad4e;
                    }
                    .report-item.info {
                    background-color: #5cb85c;
                    }
                    .report-item.error .report-item-container {
                    background-color: #f2dede;
                    }
                    .report-item.warning .report-item-container {
                    background-color: #fcf8e3;
                    }
                    .report-item.info .report-item-container {
                    background-color: #ededed;
                    }
                    .report-item-container {
                    margin-left:5px;
                    border: 1px solid #ddd;
                    border-left: 1px solid transparent;
                    border-bottom-right-radius: 4px;
                    border-top-right-radius: 4px;
                    border-bottom-left-radius: 0px;
                    border-top-left-radius: 0px;
                    padding: 8px;
                    }
                    .report-item-container .metadata {
                    margin-top: 10px;
                    }
                    .report-item-container .metadata .row {
                    margin-top: 5px;
                    }
                    .context .section-content {
                    white-space: pre-wrap;
                    display: table;
                    font-family: monospace;
                    font-size: 12px;
                    }
                    .line {
                    display: table-row;
                    }
                    .line-counter {
                    display: table-cell;
                    background-color: #ededed;
                    padding-left: 10px;
                    padding-right: 10px;
                    width: 1px;
                    text-align: center;
                    }
                    .line-content {
                    display: table-cell;
                    padding-right: 10px;
                    padding-left: 10px;
                    }
                </style>
                <div class="title">Validation report</div>
                <div class="section overview">
                    <div class="section-title">Overview</div>
                    <div class="section-content">
                        <div class="row">
                            <div class="label">Date:</div>
                            <div class="value"><xsl:value-of select="//tr:date"/></div>
                        </div>
                        <div class="row">
                            <div class="label">Result:</div>
                            <div class="value">
                                <span class="result {$result}">
                                    <xsl:choose>
                                        <xsl:when test="$result = 'FAILURE'">FAILURE</xsl:when>
                                        <xsl:when test="$result = 'WARNING'">WARNING</xsl:when>
                                        <xsl:when test="$result = 'SUCCESS'">SUCCESS</xsl:when>
                                        <xsl:otherwise>UNDEFINED</xsl:otherwise>
                                    </xsl:choose>
                                </span>
                            </div>
                        </div>
                        <div class="row">
                            <div class="label">Findings:</div>
                            <div class="value"><xsl:value-of select="//tr:counters/tr:nrOfErrors"/> error(s), <xsl:value-of select="//tr:counters/tr:nrOfWarnings"/> warning(s), <xsl:value-of select="//tr:counters/tr:nrOfAssertions"/> message(s)</div>
                        </div>
                    </div>
                </div>
                <xsl:if test="count($reportItems) > 0">
                    <div class="section details">
                        <div class="section-title">Details</div>
                        <div class="section-content">
                            <xsl:for-each select="$reportItems">
                                <xsl:variable name="severity" select="local-name()"/>
                                <div class="report-item {$severity}">
                                    <div class="report-item-container">
                                        <div class="description"><xsl:value-of select="./tr:description"/></div>
                                        <xsl:if test="count(./tr:location) = 1 or count(./tr:test) = 1 or count(./tr:assertionID) = 1">
                                            <div class="metadata">
                                                <xsl:if test="count(./tr:location) = 1">
                                                    <div class="row">
                                                        <div class="label">Location:</div><div class="value"><xsl:value-of select="./tr:location"/></div>
                                                    </div>
                                                </xsl:if>
                                                <xsl:if test="count(./tr:test) = 1">
                                                    <div class="row">
                                                        <div class="label">Test:</div><div class="value"><xsl:value-of select="./tr:test"/></div>
                                                    </div>
                                                </xsl:if>
                                                <xsl:if test="count(./tr:assertionID) = 1">
                                                    <div class="row">
                                                        <div class="label">Rule:</div><div class="value"><xsl:value-of select="./tr:assertionID"/></div>
                                                    </div>
                                                </xsl:if>
                                            </div>
                                        </xsl:if>
                                    </div>
                                </div>
                            </xsl:for-each>
                        </div>
                    </div>
                </xsl:if>
                <xsl:if test="count($input) > 0">
                    <div class="section context">
                        <div class="section-title">Validated input</div>
                        <div class="section-content">
                            <xsl:call-template name="replace-string">
                                <xsl:with-param name="text" select="$input"/>
                                <xsl:with-param name="replace" select="'&#xA;'"/>
                                <xsl:with-param name="counter" select="1"/>
                            </xsl:call-template>
                        </div>
                    </div>
                </xsl:if>
            </body>
        </html>
    </xsl:template>

    <xsl:template name="replace-string">
        <xsl:param name="text"/>
        <xsl:param name="replace"/>
        <xsl:param name="counter"/>
        <xsl:choose>
            <xsl:when test="contains($text,$replace)">
                <div class="line">
                    <div class="line-counter"><xsl:value-of select="$counter"/></div>
                    <div class="line-content"><xsl:value-of select="substring-before($text,$replace)"/></div>
                </div>
                <xsl:call-template name="replace-string">
                    <xsl:with-param name="text" select="substring-after($text,$replace)"/>
                    <xsl:with-param name="replace" select="$replace"/>
                    <xsl:with-param name="counter" select="$counter + 1"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <div class="line">
                    <div class="line-counter"><xsl:value-of select="$counter"/></div>
                    <div class="line-content"><xsl:value-of select="$text"/></div>
                </div>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
