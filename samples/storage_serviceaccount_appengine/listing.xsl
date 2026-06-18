<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ama="http://doc.s3.amazonaws.com/2006-03-01">

<xsl:template match="/">
  <html>
  <body>
  <h2><a href="http://developer.google.com/storage">Google Cloud Storage</a> Content Listing for Bucket 
      <xsl:value-of select="ama:ListBucketResult/ama:Name"/></h2>
    <table border="1" cellpadding="5">
      <tr bgcolor="#9acd32">
        <th>Object Name</th>
        <th>Modification Time</th>
        <th>ETag</th>
        <th>Size</th>
        <th>Storage Class</th>
      </tr>
      <xsl:for-each select="ama:ListBucketResult/ama:Contents">
      <tr>
        <td><xsl:value-of select="ama:Key"/></td>
        <td><xsl:value-of select="ama:LastModified"/></td>
        <td><xsl:value-of select="ama:ETag"/></td>
        <td><xsl:value-of select="ama:Size"/></td>
        <td><xsl:value-of select="ama:StorageClass"/></td>
      </tr>
      </xsl:for-each>
    </table>
  </body>
  </html>
</xsl:template>
</xsl:stylesheet>
