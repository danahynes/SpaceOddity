#!/usr/bin/env bash
#------------------------------------------------------------------------------#
# Filename: spaceoddityc.sh                                      /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/22/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# where everybody lives
INSTALL_DIR="${HOME}/.spaceoddity"

#-------------------------------------------------------------------------------
# get the stuff from the conf file
#-------------------------------------------------------------------------------

# NB: i know this is a big ugly command but it just strips leading and trailing
# whitespace and whitespace around the equals sign in case of a typo.
# generally speaking, the conf file should pass muster as a bash script so keys
# and values should have no spaces. The conf file will eventually be
# read/written through a gui which will eliminate those issues, but the file
# "could" still be written by hand, so i'll probably leave this here.
# TODO: replace this with a regex to split into key/value pairs
source <(grep = "${INSTALL_DIR}/spaceoddity.conf" | \
    sed 's/^[ \t]*//g' | sed 's/[ \t]*=[ \t]*/=/g' | sed 's/$[ \t]*//g')

#-------------------------------------------------------------------------------
# set up some variables/constants
#-------------------------------------------------------------------------------

# passed parameters
APOD_ORIGINAL_FILE="${1}"
APOD_CAPT_TEXT="${2}"

# apply required options (and defaults)
APOD_CAPT_POSITION="${POSITION:=BR}"
APOD_CAPT_COLOR="${COLOR:=rgba(255,255,255,1.0)}"
APOD_CAPT_BACKGROUND="${BACKGROUND:=rgba(0,0,0,0.75)}"

# position/size variables
# NB: all values relative to screen size. these values look good on me,
# 1920x1080. YMMV
# width of caption
APOD_CAPT_WIDTH="${WIDTH:=500}"
# font size
APOD_CAPT_FONT_SIZE="${FONT_SIZE:=15}"
# corner rounding of background
APOD_CAPT_CORNER_RADIUS="${CORNER_RADIUS:=15}"
# empty space between text and background
APOD_CAPT_BORDER="${BORDER:=20}"
# spacing between caption and top of screen (different than bottom to account
# for a top bar, if present)
APOD_CAPT_TOP_PADDING="${TOP_PADDING:=50}"
# spacing between caption and bottom of screen
APOD_CAPT_BOTTOM_PADDING="${BOTTOM_PADDING:=10}"
# spacing between caption and side of screen
APOD_CAPT_SIDE_PADDING="${SIDE_PADDING:=10}"

# ext is the last field after the last dot (single quotes for awk)
APOD_EXT=$(echo "${APOD_ORIGINAL_FILE}" | awk -F '.' '{print $NF}')

# temp file names
# colored text of a specified font size wrapped to a width on a clear background
APOD_TEXT_IMG="${INSTALL_DIR}/text.png"
# the square-cornered background with the specified color
APOD_BACK_IMG="${INSTALL_DIR}/back.png"
# the text on the square background
APOD_COMB_IMG="${INSTALL_DIR}/comb.png"
# the mask image with rounded corners
APOD_MASK_IMG="${INSTALL_DIR}/mask.png"
# the square background text image after applying the round corner mask
APOD_CAPT_IMG="${INSTALL_DIR}/capt.png"
# the wallpaper image after zooming
APOD_RESZ_IMG="${INSTALL_DIR}/apod_linux_wallpaper_resz.${APOD_EXT}"
# the wallpaper image after adding the caption
APOD_TEMP_IMG="${INSTALL_DIR}/apod_linux_wallpaper_temp.${APOD_EXT}"
# the log file - duh!
APOD_LOG_FILE="${INSTALL_DIR}/apod_linux.log"

#-------------------------------------------------------------------------------
# time to resize the original image
#-------------------------------------------------------------------------------

# get size of original image
ORIGINAL_W=$(identify -format "%[fx:w]" "${APOD_ORIGINAL_FILE}")
ORIGINAL_H=$(identify -format "%[fx:h]" "${APOD_ORIGINAL_FILE}")

# get screen resolution
# NB: must use single quotes for awk!
SCREEN_W=$(xrandr --current | grep "*" | uniq | awk '{print $1}' | cut -d "x" \
    -f1)
SCREEN_H=$(xrandr --current | grep "*" | uniq | awk '{print $1}' | cut -d "x" \
    -f2)

# get scale that zoom will use to resize desktop image
SCALE_X=$(echo "scale=2;${ORIGINAL_W}/${SCREEN_W}" | bc)
SCALE_Y=$(echo "scale=2;${ORIGINAL_H}/${SCREEN_H}" | bc)

# find smallest scale value (what scale to use to zoom original image)
SCALE="${SCALE_X}"
if (( $(echo "${SCALE_Y} < ${SCALE_X}" | bc -l) ))
then
  SCALE="${SCALE_Y}"
fi

# get scaled image size (for positioning caption)
SCALED_W=$(echo "scale=2;${ORIGINAL_W}/${SCALE}" | bc)
SCALED_H=$(echo "scale=2;${ORIGINAL_H}/${SCALE}" | bc)

# first we make the pic fit the screen (zoom to fit/fill)
convert \
  "${APOD_ORIGINAL_FILE}" \
  -resize "${SCALED_W}"x"${SCALED_H}" \
  -extent "${SCALED_W}"x"${SCALED_H}" \
  -gravity center \
  "${APOD_RESZ_IMG}" \
  >> "${APOD_LOG_FILE}" 2>&1

#-------------------------------------------------------------------------------
# The wallpaper has now been resized to "zoom" (i.e. fill the screen at the
# smallest possible size, and yes I realize that's not what most people think
# of when they hear the word "zoom", but in this context it means to scale the
# original picture UP OR DOWN until there is no blank space around the picture.)
#-------------------------------------------------------------------------------

# create the basic text image (text color on clear background)
convert \
  -size "${APOD_CAPT_WIDTH}" \
  -pointsize "${APOD_CAPT_FONT_SIZE}" \
  -fill "${APOD_CAPT_COLOR}" \
  -background none \
  -gravity west \
  caption:"${APOD_CAPT_TEXT}" \
  "${APOD_TEXT_IMG}" \
  >> "${APOD_LOG_FILE}" 2>&1

# get size of text image
TEXT_W=$(identify -format "%[fx:w]" "${APOD_TEXT_IMG}")
TEXT_H=$(identify -format "%[fx:h]" "${APOD_TEXT_IMG}")

# make new image that is x+y bigger than text image (add border)
BORDER=$(echo "scale=0;${APOD_CAPT_BORDER}+${APOD_CAPT_BORDER}" | bc)
TEXT_WB=$(echo "scale=2;${TEXT_W}+${BORDER}" | bc)
TEXT_HB=$(echo "scale=2;${TEXT_H}+${BORDER}" | bc)

# create a background for the text
convert \
  -size "${TEXT_WB}"x"${TEXT_HB}" \
  -extent "${TEXT_WB}"x"${TEXT_HB}" \
  xc:"${APOD_CAPT_BACKGROUND}" \
  "${APOD_BACK_IMG}" \
  >> "${APOD_LOG_FILE}" 2>&1

# put the text on the background
composite \
  -gravity center \
  "${APOD_TEXT_IMG}" \
  "${APOD_BACK_IMG}" \
  "${APOD_COMB_IMG}" \
  >> "${APOD_LOG_FILE}" 2>&1

# create a round rect mask same size as text image
convert \
  -size "${TEXT_WB}"x"${TEXT_HB}" \
  xc:none \
  -draw \
  "roundrectangle \
  0, \
  0, \
  ${TEXT_WB}, \
  ${TEXT_HB}, \
  ${APOD_CAPT_CORNER_RADIUS}, \
  ${APOD_CAPT_CORNER_RADIUS}" \
  "${APOD_MASK_IMG}" \
  >> "${APOD_LOG_FILE}" 2>&1

# merge background image and round rect mask
convert \
  "${APOD_COMB_IMG}" \
  -matte "${APOD_MASK_IMG}" \
  -compose DstIn \
  -composite "${APOD_CAPT_IMG}" \
  >> "${APOD_LOG_FILE}" 2>&1

# get the overhang after scaling
X_OVER=$(echo "scale=2;(${SCALED_W}-${SCREEN_W})/2" | bc)
Y_OVER=$(echo "scale=2;(${SCALED_H}-${SCREEN_H})/2" | bc)

# set the x and y pos of the caption on the image
if [ "${APOD_CAPT_POSITION}" == "TL" ]
then
  X_OFF=$(echo "scale=0;${X_OVER}+${APOD_CAPT_SIDE_PADDING}" | bc)
  Y_OFF=$(echo "scale=0;${Y_OVER}+${APOD_CAPT_TOP_PADDING}" | bc)
elif [ "${APOD_CAPT_POSITION}" == "TR" ]
then
  X_OFF=$(echo "scale=0;(${SCALED_W}-${X_OVER}-${TEXT_WB}-\
      ${APOD_CAPT_SIDE_PADDING})" | bc)
  Y_OFF=$(echo "scale=0;${Y_OVER}+\
      ${APOD_CAPT_TOP_PADDING}" | bc)
elif [ "${APOD_CAPT_POSITION}" == "BL" ]
then
  X_OFF=$(echo "scale=0;${X_OVER}+${APOD_CAPT_SIDE_PADDING}" | bc)
  Y_OFF=$(echo "scale=0;(${SCALED_H}-${Y_OVER}-${TEXT_HB}-\
      ${APOD_CAPT_BOTTOM_PADDING})" | bc)
elif [ "${APOD_CAPT_POSITION}" == "BR" ]
then
  X_OFF=$(echo "scale=0;(${SCALED_W}-${X_OVER}-${TEXT_WB}-\
      ${APOD_CAPT_SIDE_PADDING})" | bc)
  Y_OFF=$(echo "scale=0;(${SCALED_H}-${Y_OVER}-${TEXT_HB}-\
      ${APOD_CAPT_BOTTOM_PADDING})" | bc)
elif [ "${APOD_CAPT_POSITION}" == "C" ]
then
  X_OFF=$(echo "scale=0;(${SCALED_W}/2)-(${TEXT_WB}/2)" | bc)
  Y_OFF=$(echo "scale=0;(${SCALED_H}/2)-(${TEXT_HB}/2)" | bc)
fi

# merge wallpaper and caption images
convert \
  "${APOD_RESZ_IMG}" \
  "${APOD_CAPT_IMG}" \
  -geometry +"${X_OFF}"+"${Y_OFF}" \
  -compose over \
  -composite "${APOD_TEMP_IMG}" \
  >> "${APOD_LOG_FILE}" 2>&1

# move new captioned image to wallpaper
mv -f "${APOD_TEMP_IMG}" "${APOD_ORIGINAL_FILE}" \
    >> "${APOD_LOG_FILE}" 2>&1

# delete temp files
rm -f "${APOD_TEXT_IMG}" >> "${APOD_LOG_FILE}" 2>&1
rm -f "${APOD_BACK_IMG}" >> "${APOD_LOG_FILE}" 2>&1
rm -f "${APOD_COMB_IMG}" >> "${APOD_LOG_FILE}" 2>&1
rm -f "${APOD_MASK_IMG}" >> "${APOD_LOG_FILE}" 2>&1
rm -f "${APOD_CAPT_IMG}" >> "${APOD_LOG_FILE}" 2>&1
rm -f "${APOD_RESZ_IMG}" >> "${APOD_LOG_FILE}" 2>&1

# -)
