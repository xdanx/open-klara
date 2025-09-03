<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

/**
 * Custom Email Helper for KLara
 * 
 * This helper overrides the system email helper to provide better
 * email validation that supports newer TLDs like .services, .technology, etc.
 * 
 * @package		KLara
 * @subpackage	Helpers
 * @category	Helpers
 */

// ------------------------------------------------------------------------

if ( ! function_exists('valid_email'))
{
	/**
	 * Validate email address with improved TLD support
	 *
	 * This function provides better email validation than the default
	 * CodeIgniter helper by using a more comprehensive approach that
	 * supports newer TLDs and internationalized domain names.
	 *
	 * @param	string	$email
	 * @return	bool
	 */
	function valid_email($email)
	{
		// Basic format check first
		if (empty($email) || !is_string($email))
		{
			return FALSE;
		}

		// Handle internationalized domain names
		$original_email = $email;
		if (function_exists('idn_to_ascii') && strpos($email, '@'))
		{
			list($local, $domain) = explode('@', $email, 2);
			$domain = defined('INTL_IDNA_VARIANT_UTS46')
				? idn_to_ascii($domain, 0, INTL_IDNA_VARIANT_UTS46)
				: idn_to_ascii($domain);

			if ($domain !== FALSE)
			{
				$email = $local.'@'.$domain;
			}
		}

		// Split email into local and domain parts
		if (strpos($email, '@') === FALSE)
		{
			return FALSE;
		}

		// Must have exactly one @ symbol
		if (substr_count($email, '@') !== 1)
		{
			return FALSE;
		}

		list($local, $domain) = explode('@', $email, 2);

		// Validate local part (before @)
		if (empty($local) || strlen($local) > 64)
		{
			return FALSE;
		}

		// Basic local part validation - allow letters, numbers, dots, hyphens, underscores, plus
		if (!preg_match('/^[a-zA-Z0-9._+-]+$/', $local))
		{
			return FALSE;
		}

		// Local part cannot start or end with a dot
		if ($local[0] === '.' || substr($local, -1) === '.')
		{
			return FALSE;
		}

		// No consecutive dots in local part
		if (strpos($local, '..') !== FALSE)
		{
			return FALSE;
		}

		// Validate domain part (after @)
		if (empty($domain) || strlen($domain) > 253)
		{
			return FALSE;
		}

		// Domain must contain at least one dot
		if (strpos($domain, '.') === FALSE)
		{
			return FALSE;
		}

		// Domain cannot start or end with a dot or hyphen
		if ($domain[0] === '.' || substr($domain, -1) === '.' ||
			$domain[0] === '-' || substr($domain, -1) === '-')
		{
			return FALSE;
		}

		// Split domain into parts
		$domain_parts = explode('.', $domain);

		// Must have at least 2 parts (domain.tld)
		if (count($domain_parts) < 2)
		{
			return FALSE;
		}

		// Validate each domain part
		foreach ($domain_parts as $part)
		{
			if (empty($part) || strlen($part) > 63)
			{
				return FALSE;
			}

			// Each part must start and end with alphanumeric character
			// and can contain hyphens in the middle
			if (!preg_match('/^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$/', $part))
			{
				return FALSE;
			}
		}

		// TLD (last part) validation - must be at least 2 characters
		// Allow letters, numbers, and hyphens for internationalized domains (xn--)
		$tld = end($domain_parts);
		if (strlen($tld) < 2)
		{
			return FALSE;
		}

		// TLD should contain at least one letter (no purely numeric TLDs exist)
		if (!preg_match('/^[a-zA-Z0-9-]{2,}$/', $tld) || !preg_match('/[a-zA-Z]/', $tld))
		{
			return FALSE;
		}

		// Try PHP's filter_var as a secondary check, but don't fail if it rejects newer TLDs
		// This helps catch other edge cases while allowing newer TLDs to pass
		$filter_result = filter_var($original_email, FILTER_VALIDATE_EMAIL);

		// If filter_var passes, we're definitely good
		if ($filter_result !== FALSE)
		{
			return TRUE;
		}

		// If filter_var fails, check if it's likely due to a newer TLD
		// by testing with a known good TLD
		$test_email = $local . '@' . str_replace($tld, 'com', $domain);
		if (filter_var($test_email, FILTER_VALIDATE_EMAIL) !== FALSE)
		{
			// The email structure is valid, likely just a newer TLD issue
			return TRUE;
		}

		// If even the test with .com fails, the email is probably invalid
		return FALSE;
	}
}
