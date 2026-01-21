# Instructions for Coloring Your Chimera Structure

## Setup

1. **Save your AlphaFold PDB file** to:
   ```
   /Users/jeremylinsley/Documents/protein_modeling/structures/chimera_alphafold.pdb
   ```

   Or if you named it something else, you'll need to edit the script (see below).

2. **Download the coloring scripts** from the Linux server to your Mac:
   ```bash
   # On your Mac:
   scp thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/chimera_predictions/color_chimera_*.cxc ~/Documents/protein_modeling/scripts/
   ```

## Quick Start

### Option 1: Simple Coloring (Recommended to start)

```bash
cd /Users/jeremylinsley/Documents/protein_modeling/scripts
chimerax color_chimera_simple.cxc
```

This will:
- Open your structure
- Color all domains
- Let you explore interactively

### Option 2: Full Coloring + Auto-Screenshots

```bash
cd /Users/jeremylinsley/Documents/protein_modeling/scripts
chimerax color_chimera_domains.cxc
```

This will:
- Open and color your structure
- Automatically rotate and save 5 high-res images:
  - Front view
  - Side view
  - Top view
  - Dronpa close-up
  - Binding site close-up
- Save a ChimeraX session file

**Images saved to**: `/Users/jeremylinsley/Documents/protein_modeling/visualizations/`

## Color Scheme

| Domain | Residues | Color | Function |
|--------|----------|-------|----------|
| **Nanobody N-term** | 1-74 | Cyan | dATP binder (part 1) |
| Linker 1 | 75-81 | Gray | Flexible connector |
| **DRONPA** | 82-334 | **Orange** | **OPTOGENETIC SWITCH** |
| Linker 2 | 335-341 | Gray | Flexible connector |
| **Nanobody C-term** | 342-388 | Cyan | dATP binder (part 2) |
| **CDR3** | 363-369 | **Red** | **BINDING SITE** (highlighted as sticks) |
| Linker 3 | 389-393 | Gray | Flexible connector |
| **A-Catcher** | 394-409 | Green | Fluorescent readout tag |

## If Your PDB File Has a Different Name

Edit the script and change line 7:

```bash
# Open the file in a text editor:
nano /Users/jeremylinsley/Documents/protein_modeling/scripts/color_chimera_simple.cxc

# Change this line:
open /Users/jeremylinsley/Documents/protein_modeling/structures/chimera_alphafold.pdb

# To whatever your file is actually called, e.g.:
open /Users/jeremylinsley/Documents/protein_modeling/structures/my_chimera.pdb
```

## What to Look For

### Good signs:
- ✅ **Dronpa (orange) should form a β-barrel** - looks like a cylinder
- ✅ **Nanobody parts (cyan) should show β-sheet structure**
- ✅ **CDR3 (red) should be a visible loop** pointing outward
- ✅ **Linkers (gray) may look disordered** - that's normal!

### Key question:
**Can the CDR3 binding site (red) still access dATP with Dronpa inserted?**

Look at whether the red binding loop is:
- Accessible (not buried)
- Properly oriented
- Not blocked by the orange Dronpa domain

## Interactive Commands (Once Loaded)

Once the structure is open in ChimeraX, try these commands in the Command box:

```
# Hide/show specific domains
hide /A:82-334 cartoon    # Hide Dronpa
show /A:82-334 cartoon    # Show Dronpa

# Focus on specific region
view /A:363-369           # Zoom to binding site
view /A:82-334            # Zoom to Dronpa
view                      # Show full structure

# Change colors
color /A:82-334 red       # Make Dronpa red instead
color /A:82-334 orange    # Change back to orange

# Surface representation
surface                   # Show surface
~surface                  # Hide surface
```

## Comparing to Known Dronpa Structure

To see how your predicted Dronpa compares to the crystal structure:

```
# In ChimeraX:
open 2IE2                 # Opens known Dronpa crystal structure
matchmaker #1/A:82-334 to #2  # Align your Dronpa to known structure
color #2 lightblue        # Color known structure differently
```

This shows if your predicted Dronpa region matches the real structure!

## Troubleshooting

**"File not found"**:
- Check the file path in line 7 of the script
- Make sure your PDB is in the correct location
- Use full absolute paths, not `~/`

**"No such residue"**:
- AlphaFold might have numbered residues differently
- Check what residue numbers are in your PDB file
- May need to adjust the residue ranges

**Colors don't show up**:
- Make sure you're viewing in cartoon mode: `cartoon`
- Hide atoms first: `hide atoms`
- Try: `color /A cyan` to test if coloring works

---

**Once you run it, you should see**:
- Big **orange barrel** (Dronpa) in the middle
- **Cyan** nanobody parts on either side
- **Red** binding loop (CDR3) sticking out
- **Green** tag at one end (A-Catcher)

Send me a screenshot if you want help interpreting it!
