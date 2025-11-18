import pandas as pd
import requests
import os
from pathlib import Path

# IMPORTANT: Process the CSV in chunks to avoid memory issues
CHUNK_SIZE = 100000  # Process 100k rows at a time

print("="*80)
print("DOWNLOAD PHOTOS BY TAXON ID")
print("="*80)

# ============================================================================
# STEP 1: Find observations for a specific taxon_id
# ============================================================================

def find_observations_by_taxon(taxon_id, max_results=100):
    """
    Search for observations of a specific taxon
    Returns a DataFrame with matching observations
    """
    print(f"\nSTEP 1: Searching for taxon_id: {taxon_id}")
    print(f"Looking for up to {max_results} observations...")
    
    results = []
    chunk_num = 0
    
    for chunk in pd.read_csv('observations.csv', sep='\t', chunksize=CHUNK_SIZE):
        chunk_num += 1
        print(f"Scanning observations chunk {chunk_num}... (found {len(results)} so far)", end='\r')
        
        # Find matching observations in this chunk
        matches = chunk[chunk['taxon_id'] == taxon_id]
        
        # Add matches to results
        for idx, row in matches.iterrows():
            results.append(row)
            if len(results) >= max_results:
                print(f"\n✓ Found {len(results)} observations (reached max_results limit)")
                return pd.DataFrame(results)
    
    print(f"\n✓ Found {len(results)} total observations for this taxon")
    return pd.DataFrame(results) if results else None

# ============================================================================
# STEP 2: Find photos for the observation UUIDs
# ============================================================================

def find_photos_by_observation_uuids(observation_uuids):
    """
    Search for photos matching a list of observation UUIDs
    Returns a DataFrame with photo information
    """
    print(f"\nSTEP 2: Searching for photos of {len(observation_uuids)} observations...")
    
    # Convert to set for faster lookup
    uuid_set = set(observation_uuids)
    
    results = []
    chunk_num = 0
    found_uuids = set()
    
    for chunk in pd.read_csv('photos.csv', sep='\t', chunksize=CHUNK_SIZE):
        chunk_num += 1
        print(f"Scanning photos chunk {chunk_num}... (found {len(results)} photos for {len(found_uuids)} observations)", end='\r')
        
        # Find photos that match any of our observation UUIDs
        matches = chunk[chunk['observation_uuid'].isin(uuid_set)]
        
        if len(matches) > 0:
            results.append(matches)
            found_uuids.update(matches['observation_uuid'].unique())
        
        # Stop if we've found photos for all observations
        if len(found_uuids) >= len(uuid_set):
            print(f"\n✓ Found all photos!")
            break
    
    if results:
        df = pd.concat(results, ignore_index=True)
        print(f"\n✓ Found {len(df)} photos for {len(found_uuids)} observations")
        return df
    else:
        print(f"\n✗ No photos found for these observations")
        return None

# ============================================================================
# STEP 3: Download the photos
# ============================================================================

def get_photo_url(photo_id, size='medium', extension='jpg'):
    """
    Construct iNaturalist photo URL
    Sizes: original, large, medium, small, thumb, square
    """
    return f"https://inaturalist-open-data.s3.amazonaws.com/photos/{photo_id}/{size}.{extension}"

def download_photo(photo_id, size='medium', extension='jpg', output_dir='downloads'):
    """Download a single photo"""
    # Expand user path if it contains ~
    output_dir = os.path.expanduser(output_dir)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    url = get_photo_url(photo_id, size, extension)
    filename = f"{output_dir}/{photo_id}_{size}.{extension}"
    
    # Skip if already downloaded
    if os.path.exists(filename):
        return True, "already exists"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True, "downloaded"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def download_photos_from_dataframe(photos_df, size='medium', output_dir='downloads'):
    """
    Download all photos from a DataFrame
    """
    print(f"\nSTEP 3: Downloading {len(photos_df)} photos...")
    print(f"Size: {size}")
    print(f"Output directory: {output_dir}")
    
    downloaded = 0
    skipped = 0
    failed = 0
    
    for idx, row in photos_df.iterrows():
        photo_id = row['photo_id']
        extension = row['extension'] if pd.notna(row['extension']) else 'jpg'
        
        success, status = download_photo(photo_id, size=size, extension=extension, output_dir=output_dir)
        
        if success:
            if status == "downloaded":
                downloaded += 1
                print(f"[{idx+1}/{len(photos_df)}] Downloaded: {photo_id}.{extension}")
            else:
                skipped += 1
                print(f"[{idx+1}/{len(photos_df)}] Skipped (exists): {photo_id}.{extension}")
        else:
            failed += 1
            print(f"[{idx+1}/{len(photos_df)}] Failed: {photo_id}.{extension} - {status}")
    
    print(f"\n{'='*80}")
    print(f"DOWNLOAD SUMMARY:")
    print(f"{'='*80}")
    print(f"Total photos: {len(photos_df)}")
    print(f"Downloaded: {downloaded}")
    print(f"Skipped (already exists): {skipped}")
    print(f"Failed: {failed}")
    print(f"{'='*80}")

# ============================================================================
# MAIN WORKFLOW
# ============================================================================

def download_photos_by_taxon(taxon_id, max_observations=100, photo_size='medium', output_dir='downloads'):
    """
    Complete workflow: Find observations by taxon -> Find photos -> Download
    
    Args:
        taxon_id: The taxon ID to search for
        max_observations: Maximum number of observations to find
        photo_size: Size of photos to download (original, large, medium, small, thumb, square)
        output_dir: Directory to save photos
    """
    print(f"\n{'='*80}")
    print(f"WORKFLOW: Download photos for taxon_id {taxon_id}")
    print(f"{'='*80}")
    
    # Step 1: Find observations
    observations = find_observations_by_taxon(taxon_id, max_results=max_observations)
    
    if observations is None or len(observations) == 0:
        print("\n✗ No observations found for this taxon. Exiting.")
        return
    
    # Extract observation UUIDs
    observation_uuids = observations['observation_uuid'].tolist()
    print(f"\nFound {len(observation_uuids)} observation UUIDs")
    
    # Step 2: Find photos for these observations
    photos = find_photos_by_observation_uuids(observation_uuids)
    
    if photos is None or len(photos) == 0:
        print("\n✗ No photos found for these observations. Exiting.")
        return
    
    # Show photo summary
    print(f"\nPhoto breakdown:")
    print(f"  Total photos: {len(photos)}")
    print(f"  Unique observations with photos: {photos['observation_uuid'].nunique()}")
    print(f"  Photo formats: {photos['extension'].value_counts().to_dict()}")
    print(f"  Licenses: {photos['license'].value_counts().to_dict()}")
    
    # Step 3: Download photos
    download_photos_from_dataframe(photos, size=photo_size, output_dir=output_dir)
    
    print(f"\n✓ Workflow completed!")

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
  
    
    TAXON_ID = 47336  # Change this to your desired taxon
    MAX_OBSERVATIONS = 3500  # Maximum number of observations to find
    PHOTO_SIZE = 'medium'
    OUTPUT_DIR = 'Haarcascade//animals-dataset//perro' 
    
    download_photos_by_taxon(
        taxon_id=TAXON_ID,
        max_observations=MAX_OBSERVATIONS,
        photo_size=PHOTO_SIZE,
        output_dir=OUTPUT_DIR
    )