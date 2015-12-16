#!/usr/local/bin/python
"""

This is will to take the shopify product csv export and turn it into a tab delimited 
file that BorderFree can read. I'm Opting for Option3  which is 
3. Combining the Standard and Customs feeds: Optionally, you can send your Standard
and Customs feeds in a single feed file in tab-separated text or XML format.
  - Required fields: Id, title, description, category, link, image_link, dutiable_price, sale_price
  - Please note that if you choose to send a single feed file, all Customs data attributes are optional.

"""

import re
import app
import csv
import gflags as flags

BORDER_FREE_CSV_FORMAT = ('id', 'title', 'description', 'category', 'link', 'image_link', 'dutiable_price', 'sale_price', 'shipping_weight', 'color', 'size')

WEBSITE = 'http://www.aetherapparel.com/products/'
FLAGS = flags.FLAGS

flags.DEFINE_string('input_file', None, 'Input file name')
flags.MarkFlagAsRequired('input_file')

flags.DEFINE_string('output_file', None, 'Output file name')
flags.MarkFlagAsRequired('output_file')

def main(argv):
  reader = csv.reader(open(FLAGS.input_file))

  writer = csv.writer(open(FLAGS.output_file, 'w'), delimiter='\t')
  writer.writerow(BORDER_FREE_CSV_FORMAT)

  # initialize variable to check for row duplicates later.
  existing_csv_rows = {}

  # initialize variable to check for sku duplicates later.
  existing_skus = {}
  duplicate_sku_count = 0

  line_item = 0
  previous_store_link = ''

  for line in reader:
    line_item += 1

    # Map the column names for the row to BorderFree
    row = {}
    (Handle,Title,Description,Vendor,Type,Tags,Published,Option1_Name,Color,Option2_Name,Size,Option3_Name,Option3_Value,Variant_SKU,Variant_Grams,Variant_Inventory_Tracker,Variant_Inventory_Qty,Variant_Inventory_Policy,Variant_Fulfillment_Service,Variant_Price,Variant_Compare_At_Price,Variant_Requires_Shipping,Variant_Taxable,Variant_Barcode,Image_Src,Image_Alt_Text,Gift_Card,SEO_Title,SEO_Description,Google_Shopping_Google_Product_Category,Google_Shopping_Gender,Google_Shopping_Age_Group,Google_Shopping_MPN,Google_Shopping_AdWords_Grouping,Google_Shopping_AdWords_Labels,Google_Shopping_Condition,Google_Shopping_Custom_Product,Google_Shopping_Custom_Label_0,Google_Shopping_Custom_Label_1,Google_Shopping_Custom_Label_2,Google_Shopping_Custom_Label_3,Google_Shopping_Custom_Label_4,Variant_Image,Variant_Weight_Unit) = line

    # Strip potential problem characters from the beginning and end of 
    Description = Description.strip(' \t\n\r')

    # Setup the link for Border Free by combining the Website URl and the product handle
    store_link = WEBSITE + Handle

    # Handle the variants of products that don't have all details.
    # Shopify only includes all fields on the first variant of a product.
    if store_link == previous_store_link:
      published = previous_published
      title = previous_Title
      description = previous_Description
      tag_string = previous_tag_string
    else:
      previous_store_link = store_link
      published = Published
      previous_published = Published
      title = Title
      previous_Title = Title
      description = Description
      previous_Description = Description

      # Format product tags to 
      tags = Tags.strip(' \t\n\r').lower().replace(" ", "")

      print title + ' ' + tags 
      # setup the tag_string
      if 'gear' not in tags or 'doa' not in tags:
        tag_string = ''
        # Start the Category with Mens or Womens
        if 'men' in tags or 'mens' in tags:
          tag_string += 'Mens'
        elif 'women' in tags or 'womens' in tags:
          tag_string += 'Womens'
        else:
          tag_string += 'Misc'

        # Append more specifics onto the category in the Border Free syntax.
        if 'jackets' in tags:
          tag_string += ' > Jackets'
        elif 'sweaters' in tags:
          tag_string += ' > Sweaters'
        elif 'vests' in tags:
          tag_string += ' > Vests'
        elif 'sweatshirts' in tags:
          tag_string += ' > Sweatshirts'
        elif 'shirts' in tags:
          tag_string += ' > Shirts'
        elif 'baselayers' in tags:
          tag_string += ' > Base Layers'
        elif 'pantsandshorts' in tags:
          tag_string += ' > Pants and Shorts'
        elif 'swimwear' in tags:
          tag_string += ' > Swimwear'
        elif 'accessories' in tags:
          tag_string += ' > Accessories'
        elif 'archive' in tags:
          tag_string += ' > Sale'
        else:
          print title + " doesn't have a style tag?"

      else:
        tag_string = ''

      previous_tag_string = tag_string


    # Skip the row creation if it's a gift card or if it's not published to online store.
    if Gift_Card != 'true' and published == 'true' and Handle != 'gift-card' and Color != '' and tag_string != '':

      # Notify if there are duplicate skus
      if Variant_SKU in existing_skus:
        print title + ' ' + Color + ' ' + Size + " has a duplicate SKU of " + Variant_SKU
        duplicate_sku_count + 1
      else:
        existing_skus[Variant_SKU] = True

      # Strip the version tag off of the images.
      versionless_image, sep, tail = Variant_Image.partition('?v=')

      # Assign the Shopify info into the row with the correct Border Free key.
      row['id'] = Variant_SKU
      row['title'] = title
      row['description'] = description
      row['category'] = tag_string
      row['link'] = store_link
      row['image_link'] = versionless_image
      row['dutiable_price'] = Variant_Price + " USD"
      row['sale_price'] = Variant_Price + " USD"
      row['shipping_weight'] = Variant_Grams + " g"
      row['color'] = Color
      row['size'] = Size

      # Build the row and append
      csv_row = []
      for column in BORDER_FREE_CSV_FORMAT:
        if column in row:
          csv_row.append(row[column])
        else:
          csv_row.append('')

      # Convert the list to a string for comparison
      csv_row_string = str(csv_row)

      # Check to make sure that the row isn't a duplicate
      if csv_row_string not in existing_csv_rows:
        writer.writerow(csv_row)
        existing_csv_rows[csv_row_string] = True

if __name__ == '__main__':
  app.run()
